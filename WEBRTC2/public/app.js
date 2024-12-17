const videoGrid = document.getElementById("video_grid");
const muteBtn = document.getElementById("muteBtn");
const cameraoff = document.getElementById("cameraoff");
const selectCam = document.getElementById("selectCam");
const selectMic = document.getElementById("selectMic");
const screenShare = document.getElementById("screenShare");
const chatInput = document.getElementById("chat-input");
const chatForm = document.getElementById("chat-form");
const chatMessages = document.getElementById("chat-messages");

// socket init
const socket = io();

let mediaStream;
let mute = false;
let camera = true;
let currentCam;
let RTC;
let videoElements = []; // Array to store video elements and their associated IDs

// Send message when the form is submitted
chatForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const message = chatInput.value.trim();
    if (message) {
        socket.emit("send-message", message);
        chatInput.value = "";  // Clear input field
    }
});

// Event listener for new participant joining
socket.on("newJoining", (message) => showNotification(message, "join"));

// Event listener for user leaving
socket.on("userLeft", (message) => {
    showNotification(message, "leave");
    removeUserMedia(message); // Remove media when user leaves
});

// Show notification
function showNotification(message, type) {
    const notification = document.createElement("div");
    notification.classList.add("notification", type);
    notification.textContent = message;

    const notificationsContainer = document.getElementById("notifications");
    if (notificationsContainer) {
        notificationsContainer.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }
}

// Listen for incoming messages
socket.on("receive-message", (message) => {
    const messageItem = document.createElement("li");
    messageItem.textContent = message;
    chatMessages.appendChild(messageItem);
    chatMessages.scrollTop = chatMessages.scrollHeight;
});

// Sound mute handler
muteBtn.addEventListener("click", (e) => {
    if (mute) {
        mute = false;
        muteBtn.textContent = "Mute yourself";
        mediaStream.getAudioTracks().forEach(track => track.enabled = true);
    } else {
        mute = true;
        muteBtn.textContent = "Unmute yourself";
        mediaStream.getAudioTracks().forEach(track => track.enabled = false);
    }
});

// Camera off/on handler
cameraoff.addEventListener('click', () => {
    if (camera) {
        cameraoff.textContent = "Turn on camera";
        camera = false;
        mediaStream.getVideoTracks().forEach(track => track.enabled = false);
    } else {
        cameraoff.textContent = "Turn off camera";
        camera = true;
        mediaStream.getVideoTracks().forEach(track => track.enabled = true);
    }
});

// Getting the media
async function getMedia(cameraId, micId) {
    currentCam = cameraId === null ? currentCam : cameraId;

    const initialConstraints = {
        video: true,
        audio: true
    };

    const preferredCameraConstraints = {
        video: {
            deviceId: cameraId
        },
        audio: true,
    };

    const videoOption = currentCam ? {
        deviceId: currentCam
    } : true;

    const preferredMicConstraints = {
        video: videoOption,
        audio: {
            deviceId: micId
        },
    };

    try {
        mediaStream = await window.navigator.mediaDevices.getUserMedia(cameraId || micId ? cameraId ? preferredCameraConstraints : preferredMicConstraints : initialConstraints);
        displayMedia();
        getAllCameras();
        getAllMics();
        makeWebRTCConnection();

        socket.emit('joinRoom', roomId);
    } catch (error) {
        console.log(error);
    }
}

getMedia();

// Display media
function displayMedia() {
    const video = document.createElement('video');
    video.srcObject = mediaStream;

    // Add a unique ID to the video element (based on the timestamp)
    const videoId = `video-${Date.now()}`; // Unique ID based on timestamp
    video.id = videoId;

    video.addEventListener('loadedmetadata', () => {
        video.play();
    });

    videoGrid.appendChild(video);
    videoElements.push({ video, id: videoId }); // Save reference to video and ID
}

// Get all cameras
async function getAllCameras() {
    const currentCamera = mediaStream.getVideoTracks()[0];
    const allDevices = await window.navigator.mediaDevices.enumerateDevices();
    selectCam.innerHTML = '';
    allDevices.forEach(device => {
        if (device.kind === "videoinput") {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.textContent = device.label;
            option.selected = device.label === currentCamera.label ? true : false;
            selectCam.appendChild(option);
        }
    });
}

// Get all mics
async function getAllMics() {
    const currentMic = mediaStream.getAudioTracks()[0];
    const allDevices = await window.navigator.mediaDevices.enumerateDevices();
    selectMic.innerHTML = '';
    allDevices.forEach(device => {
        if (device.kind === "audioinput") {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.textContent = device.label;
            option.selected = device.label === currentMic.label ? true : false;
            selectMic.appendChild(option);
        }
    });
}

// Select a specific camera
selectCam.addEventListener('input', (e) => {
    const cameraId = e.target.value;
    getMedia(cameraId);
});

// Select a specific mic
selectMic.addEventListener('input', (e) => {
    const micId = e.target.value;
    getMedia(null, micId);
});

// Socket event listener for new joining participants
socket.on("newJoining", () => {
    makeAOffer();
});

// Make WebRTC connection
function makeWebRTCConnection() {
    RTC = new RTCPeerConnection({
        iceServers: [
            { urls: 'stun:stun1.l.google.com:19302' },
            { urls: 'stun:stun3.l.google.com:19302' },
            { urls: 'stun:stun4.l.google.com:19302' }
        ]
    });

    mediaStream.getTracks().forEach(track => {
        RTC.addTrack(track, mediaStream);
    });

    RTC.addEventListener('icecandidate', (data) => {
        socket.emit("sendIceCandidate", data.candidate, roomId);
    });

    RTC.addEventListener('addstream', (data) => {
        const videoTag = document.createElement('video');
        videoTag.srcObject = data.stream;
        videoTag.addEventListener('loadedmetadata', () => {
            videoTag.play();
        });

        videoGrid.appendChild(videoTag);
    });
}

// Make an offer
async function makeAOffer() {
    const offer = await RTC.createOffer();
    RTC.setLocalDescription(offer);
    socket.emit("sendTheOffer", offer, roomId);
}

// Receive offer
socket.on("receiveOffer", async (offer) => {
    RTC.setRemoteDescription(offer);
    const answer = await RTC.createAnswer();
    RTC.setLocalDescription(answer);
    socket.emit("sendTheAnswer", answer, roomId);
});

// Receive answer
socket.on("receiveAnswer", (answer) => {
    RTC.setRemoteDescription(answer);
});

// Receive ICE candidate
socket.on("receiveCandidate", (candidate) => {
    RTC.addIceCandidate(candidate);
});

// Remove media when user leaves
function removeUserMedia(userId) {
    // Find the video element related to the user who left
    const videoElement = videoElements.find(item => item.id === userId);
    if (videoElement) {
        // Remove the video element from the DOM
        videoElement.video.remove();
        
        // Also remove from the videoElements array
        videoElements = videoElements.filter(item => item.id !== userId);
    }
}

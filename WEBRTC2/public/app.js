const videoGrid = document.getElementById("video_grid");
const muteBtn = document.getElementById("muteBtn");
const cameraoff = document.getElementById("cameraoff");
const selectCam = document.getElementById("selectCam");
const selectMic = document.getElementById("selectMic");
const screenShare = document.getElementById("screenShare");
const chatInput = document.getElementById("chat-input");
const chatForm = document.getElementById("chat-form");
const chatMessages = document.getElementById("chat-messages");

const socket = io();

let mediaStream;
let mute = false;
let camera = true;
let currentCam;
let RTC;
let videoElements = [];

// Tambahkan event listener untuk mengirim pesan
chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (message) {
        socket.emit("send-message", message, roomId);
        chatInput.value = "";  // Bersihkan input field
        displayMessage("You: " + message);  // Tampilkan pesan sendiri
    }
});

// Terima pesan dari server
socket.on("receive-message", (message) => {
    displayMessage(message);
});

function displayMessage(message) {
    const messageItem = document.createElement("li");
    messageItem.textContent = message;
    chatMessages.appendChild(messageItem);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}



socket.on("newJoining", (message) => showNotification(message, "join"));
socket.on("userLeft", (message) => {
    showNotification(message, "leave");
    removeUserMedia(message);
});

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

socket.on("receive-message", (message) => {
    const messageItem = document.createElement("li");
    messageItem.textContent = message;
    chatMessages.appendChild(messageItem);
    chatMessages.scrollTop = chatMessages.scrollHeight;
});

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

// Event listener untuk tombol share screen
// Event listener untuk tombol share screen
// Event listener untuk tombol share screen
// Event listener untuk tombol share screen
// Event listener untuk tombol share screen
screenShare.addEventListener("click", async () => {
    try {
        const displayMediaOptions = {
            video: {
                cursor: "always"
            },
            audio: false
        };
        const screenStream = await navigator.mediaDevices.getDisplayMedia(displayMediaOptions);

        // Tambahkan track dari screen share ke peer connection
        screenStream.getTracks().forEach(track => {
            RTC.addTrack(track, screenStream);
        });
        

        const streamId = `screen-${Date.now()}`; // Berikan ID unik untuk stream
        socket.emit('startScreenShare', roomId, streamId);

        const video = document.createElement('video');
        video.srcObject = screenStream;
        video.id = streamId;
        video.addEventListener('loadedmetadata', () => {
            video.play();
        });

        videoGrid.appendChild(video);

        screenStream.getVideoTracks()[0].addEventListener('ended', () => {
            console.log('Screen sharing stopped');
            socket.emit('stopScreenShare', roomId, streamId);
            const videoElement = document.getElementById(video.id);
            if (videoElement) {
                videoElement.remove();
            }
        });
    } catch (error) {
        console.error("Error sharing screen: ", error);
    }
});

// Tambahkan elemen video baru ketika pengguna memulai berbagi layar
socket.on('userStartedScreenShare', (streamId) => {
    const video = document.createElement('video');
    video.id = streamId;
    video.autoplay = true;
    videoGrid.appendChild(video);
});

// Hapus elemen video ketika pengguna menghentikan berbagi layar
socket.on('userStoppedScreenShare', (streamId) => {
    const videoElement = document.getElementById(streamId);
    if (videoElement) {
        videoElement.remove();
    }
});

function makeAWebRTCConnection() {
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

    RTC.addEventListener('track', (event) => {
    let videoTag = document.querySelector(`#video-${event.streams[0].id}`);
    if (!videoTag) {
        videoTag = document.createElement('video');
        videoTag.srcObject = event.streams[0];
        videoTag.id = `video-${event.streams[0].id}`;
        videoTag.addEventListener('loadedmetadata', () => {
            videoTag.play();
        });
        videoGrid.appendChild(videoTag);
    }
});

}

// Tambahkan track yang baru ditambahkan dari pengguna lain
socket.on("userStartedScreenShare", (streamId) => {
    makeAWebRTCConnection();
    const video = document.createElement('video');
    video.id = streamId;
    video.autoplay = true;
    videoGrid.appendChild(video);
});



// Mendengarkan event startShareScreen dan stopShareScreen dari server
socket.on("startShareScreen", (streamId) => {
    // Buat video element untuk menampilkan share screen dari pengguna lain
    const video = document.createElement('video');
    video.id = `screen-${streamId}`;
    video.autoplay = true;
    videoGrid.appendChild(video);
});

socket.on("stopShareScreen", (streamId) => {
    // Hapus video element ketika share screen berhenti
    const videoElement = document.getElementById(`screen-${streamId}`);
    if (videoElement) {
        videoElement.remove();
    }
});




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
        makeAWebRTCConnection();

        socket.emit('joinRoom', roomId);
    } catch (error) {
        console.log(error);
    }
}

getMedia();

function displayMedia() {
    const video = document.createElement('video');
    video.srcObject = mediaStream;

    const videoId = `video-${socket.id}`; // Gunakan socket.id sebagai ID video
    video.id = videoId;

    video.addEventListener('loadedmetadata', () => {
        video.play();
    });

    videoGrid.appendChild(video);
    videoElements.push({ video, id: socket.id }); // Simpan reference ke video dan ID pengguna
}

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

selectCam.addEventListener('input', (e) => {
    const cameraId = e.target.value;
    getMedia(cameraId);
});

selectMic.addEventListener('input', (e) => {
    const micId = e.target.value;
    getMedia(null, micId);
});

socket.on("newJoining", () => {
    makeAnOffer();
});




// Make an offer
async function makeAnOffer() {
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
socket.on("userLeft", (message, userId) => {
    showNotification(message, "leave");
    removeUserMedia(userId); // Hapus video berdasarkan userId
});

function removeUserMedia(userId) {
    // Temukan elemen video yang terkait dengan pengguna yang keluar
    const videoElement = videoElements.find(item => item.id === userId);
    if (videoElement) {
        // Hapus elemen video dari DOM
        videoElement.video.remove();
        
        // Hapus dari array videoElements
        videoElements = videoElements.filter(item => item.id !== userId);
    }
}


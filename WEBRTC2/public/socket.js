// WebRTC - Client Side

// Inisialisasi peer connection dan media stream
let peerConnection;
let mediaStream;

// Mendapatkan elemen untuk video display
const videoGrid = document.getElementById("video-grid");

// Menghubungkan ke room dengan socket.emit
socket.emit('joinRoom', roomId);

socket.on("notify_new_joining", () => {
    makeAnOffer();
});

// Fungsi untuk membuat offer
async function makeAnOffer() {
    console.log("Sending offer...");
    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);
    socket.emit('makeOffer', offer, roomId);
}

// Mendapatkan offer dan membuat answer
socket.on("receiveOffer", async (offer) => {
    console.log("Receiving offer...");
    await peerConnection.setRemoteDescription(offer);
    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
    socket.emit('answer', answer, roomId);
});

// Mendapatkan answer dan menyetelnya pada peerConnection
socket.on("answer", async (answer) => {
    await peerConnection.setRemoteDescription(answer);
});

// Fungsi untuk menambah track media stream ke RTC peer connection
async function addTrackToWebRTC() {
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => {
            peerConnection.addTrack(track, mediaStream);
        });
    }
}

// Membuat koneksi RTC
function makeAWebRTCConnection() {
    peerConnection = new RTCPeerConnection();

    // Event listener untuk ICE Candidate
    peerConnection.addEventListener('icecandidate', handleCandidate);
    peerConnection.addEventListener('track', (event) => {
        console.log(event);
        const video = document.createElement('video');
        video.srcObject = event.streams[0];
        video.addEventListener('loadedmetadata', () => {
            video.play();
        });
        videoGrid.appendChild(video);
    });

    addTrackToWebRTC();
}

// Menangani ICE candidate dan mengirimkannya ke server
function handleCandidate(event) {
    if (event.candidate) {
        socket.emit('sendIceCandidate', event.candidate, roomId);
    }
}

// Mendapatkan ICE candidate dari server
socket.on("receiveCandidate", (candidate) => {
    peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
});

// Menambahkan track media ke RTC
async function addTrackToWebRTC() {
    mediaStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, mediaStream);
    });

    // Listening to ICE candidate event
    peerConnection.addEventListener('icecandidate', (event) => {
        if (event.candidate) {
            socket.emit("sendIceCandidate", event.candidate, roomId);
        }
    });
}

// Mendapatkan video stream dan menambahkannya ke RTC
async function getMediaStream() {
    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        addTrackToWebRTC();
    } catch (err) {
        console.error("Error getting media stream: ", err);
    }
}

// Panggil fungsi untuk mendapatkan media stream dari perangkat
getMediaStream();
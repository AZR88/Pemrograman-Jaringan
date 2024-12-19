const socket = io();

let mediaStream;
let peerConnection;
let videoElements = [];

// Bergabung dengan ruangan
socket.emit('joinRoom', roomId);

// Inisialisasi koneksi WebRTC
makeAWebRTCConnection();

// Event listener untuk menerima notifikasi pengguna baru bergabung
socket.on("notify_new_joining", () => {
    makeAnOffer();
});

// Membuat tawaran (offer) WebRTC
async function makeAnOffer() {
    console.log("send offer");
    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);
    socket.emit('makeOffer', offer, roomId);
}

// Menerima tawaran (offer) dari pengguna lain
socket.on("receiveOffer", async (offer) => {
    await peerConnection.setRemoteDescription(offer);
    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
    socket.emit('answer', answer, roomId);
});

// Menerima jawaban (answer) dari pengguna lain
socket.on("answer", (answer) => {
    peerConnection.setRemoteDescription(answer);
});

// Menangani ICE candidate yang diterima
socket.on("ice", (candidate) => {
    peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
});

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

        screenStream.getTracks().forEach(track => {
            peerConnection.addTrack(track, screenStream);
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

// Menambahkan elemen video baru ketika pengguna memulai berbagi layar
socket.on('userStartedScreenShare', (streamId) => {
    const video = document.createElement('video');
    video.id = streamId;
    video.autoplay = true;
    videoGrid.appendChild(video);
});

// Menghapus elemen video ketika pengguna menghentikan berbagi layar
socket.on('userStoppedScreenShare', (streamId) => {
    const videoElement = document.getElementById(streamId);
    if (videoElement) {
        videoElement.remove();
    }
});

function addTrackToWebRTC() {
    mediaStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, mediaStream);
    });
}

// Membuat koneksi WebRTC
function makeAWebRTCConnection() {
    peerConnection = new RTCPeerConnection({
        iceServers: [
            { urls: 'stun:stun1.l.google.com:19302' },
            { urls: 'stun:stun3.l.google.com:19302' },
            { urls: 'stun:stun4.l.google.com:19302' }
        ]
    });

    addTrackToWebRTC();

    peerConnection.addEventListener('icecandidate', (event) => {
        if (event.candidate) {
            socket.emit('ice', event.candidate, roomId);
        }
    });

    // Event listener untuk menangani stream yang diterima
    peerConnection.addEventListener('track', (event) => {
        const videoTag = document.createElement('video');
        videoTag.srcObject = event.streams[0];
        videoTag.addEventListener('loadedmetadata', () => {
            videoTag.play();
        });

        videoGrid.appendChild(videoTag);
    });
}

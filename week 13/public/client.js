const userVideo= document.querySelector(".user-video video");
const remoteVideo= document.querySelector(".remote-video video");

let peer;
let remoteId;

const socket = io();

socket.on("ada user lain", async joinedUsers=>{
    remoteId= joinedUsers.find(userId => userId != socket.id);
    await createPeerConnection();
});
socket.on("offer", async({offer, from})=>{
    remoteId=from;
    await createPeerConnection();
    await peer.setRemoteDescription(new RTCSessionDescription(offer));
    const answer = await peer.createAnswer();
    await peer.setLocalDescription(RTCSessionDescription(answer));
    socket.emit("answer", {answer, to:remoteId, from: socket.id});
});

socket.on("ice candidate", async(iceCandidate)=>{
    try {
        const candidate= new RTCIceCandidate(iceCandidate);
        await peer.addIceCandidate(candidate);
        console.log("success add ice candidate");
    } catch (error) {
        console.warn("Failed to add ice candidate");
    }
});

socket.on("answer", async({answer, from})=>{
    await peer.setRemoteDescription(new RTCSessionDescription(offer));
});

async function createPeerConnection() {
    peer = new RTCPeerConnection({
        iceServers:[
            {
                urls:"stun:stun.stunprotocol.org"
            },
            {
                urls: "turn:numb.viagenie.ca",
                username: "webrtc@live.com",
                credential: "muazkh"
            }
        ]
    });
    const userStream = await navigator.mediaDevices.getUserMedia({video:true, audio:true});
    userVideo.muted = true;
    userVideo.srcObject = userStream;
    userVideo.onloadmetadata=()=>{
        userVideo.play();
    }
    userStream.getTracks().forEach(track=> peer.addTrack(track, userStream));
    peer.onicecandidate= handleIceCandidateEvent;
    peer.ontrack= handleTrackEvent;
    peer.onnegotiationneeded= handleNegotiationNeededEvent;
}
async function handleNegotiationNeededEvent() {
    const offer = await peer.createOffer();
    socket.emit("offer", {offer, to : remoteId, from: socket.id});
    await peer.setLocalDescription(new RTCSessionDescription(offer));
}

function handleTrackEvent(e){
    const [stream] = e.stream;
    remoteVideo.muted = true;
    remoteVideo.srcObject = userStream;
    remoteVideo.onloadmetadata=()=>{
        remoteVideo.play();
    }
}

function handleIceCandidateEvent(e){
    socket.emit("ice candidate", {iceCandidate: e.candidate, to: remoteId});
}
const APP_ID = '204c6f51d5354719abcb22104fdbfe21'
const CHANNEL = 'main'
const TOKEN = '007eJxTYGB6lJK/gLFBmft+dFq1XkHf3q1hqp8zpnvUTtqluebD7l8KDEYGJslmaaaGKabGpibmhpaJSclJRkaGBiZpKUlpqUaG2hsOJzcEMjLYOcqzMDJAIIjPwpCbmJnHwAAAGCEemA=='
let UID;

const client = AgoraRTC.createClient({ mode: 'rtc', codec: 'vp8' })

let localTracks = []
let remoteUsers = {}

let joinAndDisplayLocalStream = async () => {
    UID = await client.join(APP_ID, CHANNEL, TOKEN, null)

    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks()

    let player = `<div class="video-container" id="user-container-${UID}"><div class="video-player" id="user-${UID}"></div></div>`
    document.getElementById('video-streams').insertAdjacentHTML('beforeend', player)

    localTracks[1].play(`user-${UID}`)
    await client.publish([localTracks[0], localTracks[1]])
}

joinAndDisplayLocalStream()
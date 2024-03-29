function createCallFrame() {
    callFrame = window.DailyIframe.wrap(document.getElementById('daily-co'), {
        showLeaveButton: true,
        iframeStyle: {
            position: 'fixed',
            top: '0',
            left: '0',
            height: '100%',
            width: '100%',
            border: 'none',
        },
        theme: {
            colors: {
                "accent": "#AFD5CF",
                "accentText": "#000000",
                "background": "#1A1A1A",
                "backgroundAccent": "#2F2F2F",
                "baseText": "#F5F5F5",
                "border": "#444444",
                "mainAreaBg": "#262626",
                "mainAreaBgAccent": "#333333",
                "mainAreaText": "#F5F5F5",
                "supportiveText": "#B3B3B3"
            }
        }
    });
    callFrame.join({ url: '{{ url }}', userName: '{{ username }}', token: '{{ token }}' });
    callFrame.on('loaded', (event) => {
        // Make a request to the server to update the user's status to in a call
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/user_in/');
        xhr.setRequestHeader('Content-Type', 'application/json');
        const url = window.location.href;
        // Get only the room name from the url
        const room_id = '{{ room_id }}';
        console.log(room_id);
        xhr.send(JSON.stringify({ 'room_id': room_id }));
        xhr.onload = () => {
            if (xhr.status != 200) {
                alert(`Error ${xhr.status}: ${xhr.statusText}`);
            }
            else if (xhr.responseText != 'Success') {
                alert(`Error: ${xhr.responseText}`);
            }
            else {
                console.log('User status updated to in a call');
            }
        };

    });
    let timerId = null;

    callFrame.on('participant-left', event => {
        timerId = setTimeout(() => {
            // leave the callframe if the timer expires
            callFrame.leave();
            window.location.href = '/call'
        }, 5000); // 5 seconds
    });

    callFrame.on('participant-joined', event => {
        // clear the timer if the join event is triggered within the time period
        if (timerId) {
            clearTimeout(timerId);
            timerId = null;
        }
    });
    callFrame.on('left-meeting', event => {
        window.location.href = '/call'
    });
}
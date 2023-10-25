document.addEventListener('DOMContentLoaded', function () {
    const localView = document.getElementById('localView');
    const outputView = document.getElementById('outputView');
    const videoConstraints = {
        width: { ideal: 640 },
        height: { ideal: 360 },
    };

    let localStream;
    let webSocket;

    function connectSocket() {
        let ws_scheme = window.location.protocol == "https:" ? "wss://" : "ws://";
        webSocket = new WebSocket(
            ws_scheme + window.location.host + '/ws/live_dehaze/'
        );

        webSocket.onopen = (event) => {
            console.log('WebSocket connection opened');
            setInterval(captureFrame, 250);
        };

        webSocket.onmessage = (event) => {
            const blob = new Blob([event.data], {type: 'image/jpeg'});
            const url = URL.createObjectURL(blob);
            outputView.src = url;
            // URL.revokeObjectURL(url);
        };
    }

    function startCamera() {
        navigator.mediaDevices.getUserMedia({ video: videoConstraints })
            .then(stream => {
                localStream = stream;
                localView.srcObject = stream;
                connectSocket();
            })
            .catch(error => {
                console.error('Error accessing the camera:', error);
            });
    }

    function captureFrame() {
        const canvas = document.createElement('canvas');
        canvas.width = localView.videoWidth;
        canvas.height = localView.videoHeight;
        const context = canvas.getContext('2d');
        context.drawImage(localView, 0, 0, canvas.width, canvas.height);
    
        // Convert the canvas image to a Blob object
        canvas.toBlob(function(blob) {
            // Send the Blob object to the server
            webSocket.send(blob);
        }, 'image/jpeg');
    }
    

    function stopCameraAndWebSocket() {
        if (localStream) {
            localStream.getTracks().forEach(track => track.stop());
        }
        if (webSocket) {
            webSocket.close();
        }
    }

    // Handle stopping both media recording and the WebSocket connection
    window.onbeforeunload = stopCameraAndWebSocket;

    // Capture a frame from the video stream every 1000ms
    startCamera();

});
    
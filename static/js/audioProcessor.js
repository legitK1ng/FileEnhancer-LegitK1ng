class AudioProcessor {
    constructor() {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }

    async visualizeAudio(audioBuffer) {
        const canvas = document.createElement('canvas');
        canvas.width = 800;
        canvas.height = 200;
        const ctx = canvas.getContext('2d');
        
        const data = audioBuffer.getChannelData(0);
        const step = Math.ceil(data.length / canvas.width);
        const amp = canvas.height / 2;
        
        ctx.fillStyle = 'var(--bs-dark)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.beginPath();
        ctx.moveTo(0, amp);
        ctx.strokeStyle = 'var(--bs-info)';
        
        for (let i = 0; i < canvas.width; i++) {
            const min = Math.min(...data.slice(i * step, (i + 1) * step));
            const max = Math.max(...data.slice(i * step, (i + 1) * step));
            ctx.lineTo(i, amp + min * amp);
            ctx.lineTo(i, amp + max * amp);
        }
        
        ctx.stroke();
        return canvas;
    }

    async loadAudioFile(file) {
        const arrayBuffer = await file.arrayBuffer();
        const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);
        return audioBuffer;
    }
}

const audioProcessor = new AudioProcessor();

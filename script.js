document.addEventListener("DOMContentLoaded", () => {
    const flagCanvas = document.getElementById("flagCanvas");
    const ctx = flagCanvas.getContext("2d");
    const optionButtons = [
        document.getElementById("option1"),
        document.getElementById("option2"),
        document.getElementById("option3"),
        document.getElementById("option4")
    ];
    const progressLabel = document.getElementById("progress");
    const correctSound = document.getElementById("correctSound");
    const errorSound = document.getElementById("errorSound");

    let countries = paises.countries;
    let currentCountry = null;
    let remainingCountries = [...countries];
    let correctAnswers = 0;
    let wrongAnswers = 0;

    function loadFlag(country) {
        const img = new Image();
        img.src = `${country}_sombra.png`;
        img.onload = () => {
            ctx.clearRect(0, 0, flagCanvas.width, flagCanvas.height);
            ctx.drawImage(img, 0, 0, flagCanvas.width, flagCanvas.height);
        };
        img.onerror = () => {
            console.error(`No se pudo cargar la imagen para ${country}`);
            ctx.clearRect(0, 0, flagCanvas.width, flagCanvas.height);
            ctx.fillStyle = '#ccc';
            ctx.fillRect(0, 0, flagCanvas.width, flagCanvas.height);
            ctx.fillStyle = '#000';
            ctx.font = '20px Arial';
            ctx.fillText('Imagen no disponible', 100, 200);
        };
    }

    function nextQuestion() {
        if (remainingCountries.length === 0) {
            alert("Se han utilizado todos los países disponibles. Reiniciando la lista.");
            remainingCountries = [...countries];
        }
        currentCountry = remainingCountries.splice(Math.floor(Math.random() * remainingCountries.length), 1)[0];
        loadFlag(currentCountry);

        let options = countries.filter(country => country !== currentCountry);
        options = options.sort(() => 0.5 - Math.random()).slice(0, 3);
        options.push(currentCountry);
        options = options.sort(() => 0.5 - Math.random());

        optionButtons.forEach((button, index) => {
            button.textContent = options[index];
            button.onclick = () => checkAnswer(options[index]);
        });
    }

    function checkAnswer(selectedCountry) {
        if (selectedCountry === currentCountry) {
            correctAnswers++;
            correctSound.play();
        } else {
            wrongAnswers++;
            errorSound.play();
        }
        loadFlagNormal(currentCountry);
        updateProgress();

        if (wrongAnswers >= 3) {
            setTimeout(() => {
                alert("Has cometido 3 errores. Fin del juego.");
                resetGame();
            }, 1000);
        } else if (correctAnswers >= 10) {
            setTimeout(() => {
                alert("¡Felicidades! Has acertado 10 veces.");
                resetGame();
            }, 1000);
        } else {
            setTimeout(nextQuestion, 2000);
        }
    }

    function loadFlagNormal(country) {
        const img = new Image();
        img.src = `${country}.png`;
        img.onload = () => {
            ctx.clearRect(0, 0, flagCanvas.width, flagCanvas.height);
            ctx.drawImage(img, 0, 0, flagCanvas.width, flagCanvas.height);
        };
        img.onerror = () => {
            console.error(`No se pudo cargar la imagen para ${country}`);
            ctx.clearRect(0, 0, flagCanvas.width, flagCanvas.height);
            ctx.fillStyle = '#ccc';
            ctx.fillRect(0, 0, flagCanvas.width, flagCanvas.height);
            ctx.fillStyle = '#000';
            ctx.font = '20px Arial';
            ctx.fillText('Imagen no disponible', 100, 200);
        };
    }

    function updateProgress() {
        progressLabel.textContent = `Aciertos: ${correctAnswers} / Errores: ${wrongAnswers}`;
    }

    function resetGame() {
        remainingCountries = [...countries];
        correctAnswers = 0;
        wrongAnswers = 0;
        updateProgress();
        nextQuestion();
    }

    nextQuestion();
});
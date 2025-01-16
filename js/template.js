function displayPlays(playData, weekNo) {
    const container = document.getElementById("play-container");
    container.innerHTML = ""; // Clear loading message

    playData.forEach((play, index) => {
      const playCard = document.createElement("div");
      playCard.classList.add("play-card");

      // Image URL with dynamic play number
      const imageUrl = `https://media.githubusercontent.com/media/arnavk377/hookedonfalconsplays/refs/heads/main/gameshots/week${weekNo}/play${index + 1}.png`;

      playCard.innerHTML = `
        <h2>Play #${index + 1} - Quarter ${play.quarter}</h2>
        <p><strong>Time:</strong> ${play.time}</p>
        <p><strong>Possession:</strong> ${play.possession}</p>
        <p><strong>Position:</strong> ${play.position > 0 ? `+${play.position}` : play.position}</p>
        <p><strong>Down:</strong> ${play.down}</p>
        <p><strong>Yards to Go:</strong> ${play.yardage}</p>
        <p><strong>Play Type:</strong> ${play.playType}</p>
        <p><strong>Details:</strong> ${play.details}</p>
        <p><strong>Description:</strong> ${play.description}</p>
        <a href="${imageUrl}" target="_blank">
          <img src="${imageUrl}" alt="Play ${index + 1} Screenshot">
        </a>
      `;

      container.appendChild(playCard);
    });
}
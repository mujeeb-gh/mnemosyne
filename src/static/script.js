const captureImage = () => {
  const video = document.getElementById("video");
  const canvas = document.createElement("canvas");
  canvas.width = video.width;
  canvas.height = video.height;

  const context = canvas.getContext("2d");
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  const imageData = canvas.toDataURL("image/jpeg");

  fetch("/capture", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      image: imageData,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      const statusDiv = document.getElementById("status");
      if (data.error) {
        statusDiv.className = "error";
        statusDiv.textContent = data.error;
      } else {
        statusDiv.className = "success";
        statusDiv.textContent = `${data.message} Quality: ${data.quality}, Anti-Spoofing: ${data.anti_spoofing_confidence}`;
      }
    })
    .catch((error) => {
      const statusDiv = document.getElementById("status");
      statusDiv.className = "error";
      statusDiv.textContent = "Error: " + error.message;
    });
}

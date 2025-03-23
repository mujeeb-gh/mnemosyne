const navigateTo = (page) => {
  window.location.href = `/${page}`;
};

const captureImage = () => {
  const video = document.getElementById("video");
  const canvas = document.createElement("canvas");
  canvas.width = video.width;
  canvas.height = video.height;

  const context = canvas.getContext("2d");
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  const imageData = canvas.toDataURL("image/jpeg");

  fetch("/face/capture", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      image: imageData,
    }),
  })
    .then((response) => response.json().then((data) => ({ status: response.status, body: data })))
    .then(({ status, body }) => {
      const statusDiv = document.getElementById("status");
      const captureButton = document.getElementById("captureButton");
      const tryAgainButton = document.getElementById("tryAgainButton");
      const confirmButton = document.getElementById("confirmButton");
      if (status !== 200) {
        statusDiv.className = "error";
        statusDiv.textContent = body.error || body.message;
        captureButton.style.display = "none";
        tryAgainButton.style.display = "block";
        confirmButton.disabled = true;
      } else {
        statusDiv.className = "success";
        statusDiv.textContent = `${body.message} Quality: ${body.quality}, Anti-Spoofing: ${body.anti_spoofing_confidence}`;
        tryAgainButton.style.display = "none";
        confirmButton.disabled = false;
      }
    })
    .catch((error) => {
      const statusDiv = document.getElementById("status");
      statusDiv.className = "error";
      statusDiv.textContent = "Error: " + error.message;
      const captureButton = document.getElementById("captureButton");
      const tryAgainButton = document.getElementById("tryAgainButton");
      const confirmButton = document.getElementById("confirmButton");
      captureButton.style.display = "none";
      tryAgainButton.style.display = "block";
      confirmButton.disabled = true;
    });
};

const confirmCapture = () => {
  // Implement the logic for confirming the capture
  alert("Capture confirmed!");
};

const submitRegistration = () => {
  const form = document.getElementById("registerForm");
  if (!form.checkValidity()) {
    return;
  }

  const matric_no = document.getElementById("matric_no").value;
  const name = document.getElementById("name").value;
  const email = document.getElementById("email").value;
  const program = document.getElementById("program").value;
  const year_of_study = document.getElementById("year_of_study").value;
  const date_of_birth = document.getElementById("date_of_birth").value;
  const phone_number = document.getElementById("phone_number").value;

  const data = {
    matric_no,
    name,
    email,
    program,
    year_of_study,
    date_of_birth,
    phone_number,
  };

  fetch("/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then((response) => response.json())
    .then((data) => {
      const statusDiv = document.getElementById("status");
      if (data.error) {
        statusDiv.className = "error";
        statusDiv.textContent = data.error;
      } else {
        statusDiv.className = "success";
        statusDiv.textContent = data.message;
      }
    })
    .catch((error) => {
      const statusDiv = document.getElementById("status");
      statusDiv.className = "error";
      statusDiv.textContent = "Error: " + error.message;
    });

  navigateTo("face/capture");
};

const changeVideoSource = () => {
  const videoSourceSelect = document.getElementById("videoSourceSelect");
  const ipWebcamUrlInput = document.getElementById("ipWebcamUrl");
  const video = document.getElementById("video");

  if (videoSourceSelect.value === "ip") {
    ipWebcamUrlInput.style.display = "block";
    video.setAttribute("src", "");
    const ipWebcamUrl = ipWebcamUrlInput.value;
    if (ipWebcamUrl) {
      video.setAttribute(
        "src",
        `/video?source=${encodeURIComponent(ipWebcamUrl)}&t=${Date.now()}`
      );
    }
  } else if (videoSourceSelect.value === "default") {
    ipWebcamUrlInput.style.display = "none";
    video.setAttribute("src", `/video?t=${Date.now()}`); // This will use the default camera (source=0)
  }
};

// Handle IP webcam URL changes
document.getElementById("ipWebcamUrl").addEventListener("input", () => {
  const videoSourceSelect = document.getElementById("videoSourceSelect");
  if (videoSourceSelect.value === "ip") {
    const ipWebcamUrl = document.getElementById("ipWebcamUrl").value;
    const video = document.getElementById("video");
    if (ipWebcamUrl) {
      video.src = `/video?source=${ipWebcamUrl}/video`;
    }
  }
});

// Add event listener for video source selection changes
document
  .getElementById("videoSourceSelect")
  .addEventListener("change", changeVideoSource);

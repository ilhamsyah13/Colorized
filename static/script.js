document.querySelectorAll(".dropzone-input").forEach((inputElement) => {
  const dropZoneElement = inputElement.closest(".dropzone");

  dropZoneElement.addEventListener("click", (e) => {
    inputElement.click();
  });

  inputElement.addEventListener("change", (e) => {
    if (inputElement.files.length) {
      updateThumbnail(dropZoneElement, inputElement.files[0]);
    }
  });

  dropZoneElement.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZoneElement.classList.add("dropzone--over");
  });

  dropZoneElement.addEventListener("drop", (e) => {
    e.preventDefault();

    if (e.dataTransfer.files.length) {
      inputElement.files = e.dataTransfer.files;
      updateThumbnail(dropZoneElement, e.dataTransfer.files[0]);
    }

    dropZoneElement.classList.remove("dropzone--over");
  });
});

function updateThumbnail(dropZoneElement, file) {
  let thumbnailElement = dropZoneElement.querySelector(".dropzone-image");

  if (dropZoneElement.querySelector(".dropzone-label")) {
    dropZoneElement.querySelector(".dropzone-label").remove();
    thumbnailElement = document.createElement("div");
    thumbnailElement.classList.add("dropzone-image");
    dropZoneElement.appendChild(thumbnailElement);
  }

  const reader = new FileReader();
  reader.readAsDataURL(file);
  reader.onload = () => {
    thumbnailElement.style.backgroundImage = `url('${reader.result}')`;
  };
}

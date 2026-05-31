let currentSlideIndex = 0;
const slides = document.querySelectorAll(".slide");
let slideTimer = null;

function showSlide(index) {
    if (slides.length === 0) {
        return;
    }

    slides.forEach((slide) => {
        slide.classList.remove("active");
    });

    const activeSlide = slides[index];
    activeSlide.classList.add("active");

    const duration = parseInt(activeSlide.dataset.duration || "15000", 10);

    if (slideTimer) {
        clearTimeout(slideTimer);
    }

    slideTimer = setTimeout(() => {
        currentSlideIndex = (currentSlideIndex + 1) % slides.length;
        showSlide(currentSlideIndex);
    }, duration);
}

document.addEventListener("DOMContentLoaded", () => {
    if (slides.length > 0) {
        showSlide(0);
    }
});
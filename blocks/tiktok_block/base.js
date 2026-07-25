document.addEventListener("DOMContentLoaded", () => {
  const container = document.querySelector('.tiktok-video_viewport');
  const slides = document.querySelectorAll('.tiktok-video_slide');

  function update() {
    const containerRect = container.getBoundingClientRect();
    const containerCenter = containerRect.left + containerRect.width / 2;

    slides.forEach(slide => {
      const rect = slide.getBoundingClientRect();
      const slideCenter = rect.left + rect.width / 2;

      const isActive = Math.abs(containerCenter - slideCenter) < rect.width / 2;

      slide.classList.toggle('active', isActive);
    });
  }

  container.addEventListener('scroll', () => {
    requestAnimationFrame(update);
  });

  update();
});






// Dependecy inversion anchor
// lock to tiktok, to cookie_consent_v2
function ApplyConsentPolicyTiktok(consentDict) {
  try {

    const videoBlock = document.getElementById("tiktok-video_id");
    const mockBlock = document.getElementById("tiktok-mock");

    const allowed =
      consentDict?.statistics === true &&
      consentDict?.marketing === true;

    console.log("ApplyConsentPolicyTiktok called!");

    if (allowed) {
      console.log("[Consent] allowed → show TikTok");

      if (videoBlock) videoBlock.style.display = "flex";
      if (mockBlock) mockBlock.style.display = "none";

      // правильне підключення TikTok embed
      if (!document.querySelector('script[src="https://www.tiktok.com/embed.js"]')) {
        const script = document.createElement("script");
        script.src = "https://www.tiktok.com/embed.js";
        script.async = true;
        document.body.appendChild(script);
      }

    } else {
      console.log("[Consent] blocked → show mock", consentDict);

      if (videoBlock) videoBlock.style.display = "none";
      if (mockBlock) mockBlock.style.display = "block";
    }

  } catch (e) {
    console.error("[Consent] error applying TikTok policy", e);

    const videoBlock = document.getElementById("tiktok-video_id");
    const mockBlock = document.getElementById("tiktok-mock");

    if (videoBlock) videoBlock.style.display = "none";
    if (mockBlock) mockBlock.style.display = "block";
  }
}


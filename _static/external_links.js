$(function () {
  $("a.external").each(function () {
    const u = new URL(this.href, location.origin);
    if (
      u.hostname !== "ramppdev.github.io" ||
      !u.pathname.startsWith("/ablate")
    )
      $(this).attr({ target: "_blank", rel: "noopener noreferrer" });
  });
});

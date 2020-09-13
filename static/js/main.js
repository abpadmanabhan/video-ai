$(document).ready(function () {
  // display login form
  $(".welcome .primary").click(function () {
    $(".welcome").hide();
    $("form").fadeIn();
  });

  // display welcome
  $("form .minor").click(function () {
    $("form").hide();
    $(".welcome").fadeIn();
  });

  // form validation
  var validateLogin = function () {
    var username = $.trim($(".field input[name=username]").val());
    var password = $.trim($(".field input[name=password]").val());

    if (username.length > 0 && password.length > 0) {
      $("form .primary").removeClass("disabled");
    } else {
      $("form .primary").addClass("disabled");
    }
  };
  validateLogin();
  $(".field input").keyup(validateLogin);

  // header
  var $toggleButton = $(".toggle-button");
  var $navbarLinks = $(".navbar-links");

  $toggleButton.click(function () {
    $navbarLinks.toggleClass("active");
  });

  $(document).click(function (e) {
    if (
      !$(e.target).closest("a").length &&
      !$(e.target).is("a") &&
      !$(e.target).closest(".active").length
    ) {
      $(".active").removeClass("active");
    }
  });

  // video
  $(document).on("click", "video", function () {
    this.paused ? this.play() : this.pause();
  });

  // upload
  $("#upload-form").on("change", "input[type='file']", function (e) {
    var fileName = this.files && this.files[0] && this.files[0].name;
    if (fileName) {
      $(this).siblings("label").text(fileName).addClass("selected");
    } else {
      $(this).siblings("label").text("Choose").removeClass("selected");
      $(e.target).text("Choose");
    }
    var source = $.trim($(".field input[name=source]").val());
    var driver = $.trim($(".field input[name=driver]").val());
    if (source.length > 0 && driver.length > 0) {
      $(this).closest("form").find(".primary").removeClass("disabled");
    } else {
      $(this).closest("form").find(".primary").addClass("disabled");
    }
  });

  // select form
  $("#select-form").on("change", "input[type='radio']", function (e) {
    var source = $.trim($(this).closest("form").find("input[name=source]").val());
    var driver = $.trim($(this).closest("form").find("input[name=driver]").val());
    if (source.length > 0 && driver.length > 0) {
      $(this).closest("form").find(".primary").removeClass("disabled");
    } else {
      $(this).closest("form").find(".primary").addClass("disabled");
    }
  });

  $(".tabs .tab").click(function () {
    $(this)
      .siblings()
      .each(function () {
        var id = $(this).data("toggle-area");
        $(this).removeClass("current");
        $("#" + id).hide();
      });
    var currentTabId = $(this).data("toggle-area");
    $(this).addClass("current");
    $("#" + currentTabId).show();
  });
});

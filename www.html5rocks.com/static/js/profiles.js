$(function() {
  function updateHash(e) {
    $activeProfile = $(".active");
    if ($activeProfile.length) {
      history.replaceState({}, document.title, '/profiles/#!/' + $activeProfile.attr("id"));
    } else {
      if (!!window.history) {
        history.replaceState({}, document.title, '/profiles');
      } else {
        location.hash = "/#!/"; // oh well, old browsers have to live with a #
      }
    }
  }

  window.showArticles = function(link) {
    var $profile = $(link).closest('.profile');
    $profile.find('.back').toggleClass('active');
    $profile.find('.front').toggleClass('active');
    return false;
  };

  $('.profile .list-articles').click(function(e) {
    var $profile = $(this).closest('.profile');
    $profile.find('.back').toggleClass('active');
    $profile.find('.front').toggleClass('active');
    e.stopPropagation();
    return false;
  });

  window.scrollToProfile = function(opt_profileID) {
    var profileID = opt_profileID || null;
    if (!profileID && location.hash.length) {
      profileID = '#' + location.hash.split('#!/')[1];
    }
    if (profileID) {
      $.scrollTo(profileID, 800, {offset: {top: -12}, onAfter: function() {
        $(profileID).addClass("active");
      }});
    }
  };

  $(".profile").click(function(e) {
    $(".profile").not(this).removeClass("active");
    $(this).toggleClass("active");
    $(this).find('.back').removeClass('active');
    $(this).find('.front').removeClass('active');
    updateHash(e);
    e.stopPropagation();
  });

  $(window).click(function(e) {
    $(".profile").removeClass("active");
    $(".profile").find('.back').removeClass('active');
    $(".profile").find('.front').removeClass('active');
    updateHash(e);
  });

  function onHashChange(profileID) {
    $(".profile").removeClass("active");
    window.scrollToProfile(profileID);
  }

  window.onhashchange = function(e) {
    if (!location.hash.length) {
      return;
    }
    onHashChange('#' + location.hash.split('/#!/')[1]);
  };

});

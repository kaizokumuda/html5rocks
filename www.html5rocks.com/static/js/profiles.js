$(function() {
  function updateHash(e) {
    e.preventDefault();
    e.stopPropagation();

    $activeProfile = $(".active");
    if ($activeProfile.length) {
      //location.hash = '!/' + $activeProfile.attr("id");
      history.replaceState({}, document.title, '/profiles/#!/' + $activeProfile.attr("id"));
    } else {
      if (!!window.history) {
        history.replaceState({}, document.title, '/profiles/#!/');
      } else {
        location.hash = "/#!/"; // oh well, old browsers have to live with a #
      }
    }
  }

  window.slideMap = function(el) {
    $(el).toggleClass('active');
  };

  window.scrollToProfile = function(opt_profileID) {
    var profileID = opt_profileID || null;
    if (!profileID && location.hash.length) {
      profileID = '#' + location.hash.split('#!/')[1];
    }
    if (profileID) {
      $.scrollTo(profileID, 800, {offset: {top: -12}, onAfter: function() {
        $(profileID).addClass("active");
      }});
      //window.onhashchange(); // run on page load
    }
  };

  $(".profile").click(function(e) {
    $(".profile").not(this).removeClass("active");
    $(this).addClass("active");
    updateHash(e);
    //onHashChange('#' + $(this).attr('id'));
    return false;
  });

  $(window).click(function(e) {
    $(".profile").removeClass("active");
    updateHash(e);
  });

  function onHashChange(profileID) {
    $(".profile").removeClass("active");

    window.scrollToProfile(profileID);

    //$("#" + profileID).addClass("active");
  }

  window.onhashchange = function(e) {
    if (!location.hash.length) {
      return;
    }
    onHashChange('#' + location.hash.split('/#!/')[1]);
  };

});

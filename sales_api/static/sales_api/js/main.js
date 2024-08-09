$(document).ready(function() {

  // NAVIGATION BURGER
  $('.navbar-burger').click(function() {
    $(this).toggleClass('is-active');

    var $menu = $('.navbar-menu');
    if ($menu.hasClass('is-active')) {
        $menu.slideUp(300, function() {
            $menu.removeClass('is-active');
        });
    } else {
        $menu.slideDown(300, function() {
            $menu.addClass('is-active');
        });
    }
  });


  // THEME TOGGLE
  function setTheme(theme, name, icon) {
    $('html').attr('data-theme', theme);
    $('#theme-name').text(name);
    $('#theme-icon').attr('class', icon);
    localStorage.setItem('theme', theme);
    localStorage.setItem('themeName', name);
    localStorage.setItem('themeIcon', icon);
  }

  $('#theme-toggle').on('click', function() {
    var currentTheme = $('html').attr('data-theme');
    var newTheme = (currentTheme === 'light') ? 'dark' : 'light';
    var themeName = (newTheme === 'light') ? 'Light' : 'Dark';
    var themeIcon = (newTheme === 'light') ? 'fa-solid fa-sun fa-flip' : 'fa-solid fa-moon fa-flip';
    
    setTheme(newTheme, themeName, themeIcon);
  });

  // On page load, set theme based on localStorage or default to light
  var savedTheme = localStorage.getItem('theme') || 'light';
  var themeName = localStorage.getItem('themeName') || 'Light';
  var themeIcon = localStorage.getItem('themeIcon') || 'fa-solid fa-sun fa-flip';
  
  setTheme(savedTheme, themeName, themeIcon);


  // BACK BUTTON
  $('#cancel-button').attr('href', document.referrer || '/home');


  // ICON HOVER
  function toggleHoverClass(element, className) {
    $(element).hover(function() {
      $(this).find('i').addClass(className);
    }, function() {
      $(this).find('i').removeClass(className);
    });
  }

  toggleHoverClass('.menu-list li', 'fa-beat-fade');
  toggleHoverClass('.button', 'fa-beat-fade');


  // MODAL
  $(".modal-content, .modal-background").hide();

  function openModal(dataId, dataName) {
    $('#itemName').text(dataName);
    $('#itemId').val(dataId);
    
    $('#modal-js').addClass('is-active');
    $(".modal-background").fadeIn(250);
    $(".modal-content").fadeIn(400);
  }

  function closeModal() {
    $(".modal-background").fadeOut(250);
    $(".modal-content").fadeOut(400, function() {
      $('.modal').removeClass('is-active');
    });
  }

  // Modal Open
  $(".modal-button").click(function() {
    openModal($(this).data("id"), $(this).data("name"));
  });

  // Modal Close
  $('.modal-background, .modal-content .button').click(closeModal);
  $(document).on("keydown", function(event) {
    if (event.key === "Escape") {
      closeModal();
    }
  });

});
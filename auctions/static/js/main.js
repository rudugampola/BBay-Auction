const spinnerBox = document.getElementById('spinner-box');
const data = document.getElementById('data-box');

// console.log(spinnerBox);
// console.log(data);

if (spinnerBox && data) {
  document.addEventListener('DOMContentLoaded', function () {
    setTimeout(() => {
      spinnerBox.classList.add('not-visible');
      data.classList.remove('not-visible');
    }, 1000);
  });
}

// if (spinnerBox) {
//   $.ajax({
//     // type: 'GET',
//     // url: '/expenses',
//     success: function (response) {
//       setTimeout(() => {
//         spinnerBox.classList.add('not-visible');
//         data.classList.remove('not-visible');
//       }, 500);
//     },
//     error: function (error) {
//       setTimeout(() => {
//         dataBox.innerHTML = '<b>Failed to load data</b>';
//       }, 500);
//     },
//   });
// }

const spinnerLoading = document.getElementById('spinner-loading');
const dataLoading = document.getElementById('data-loading');

if (spinnerLoading && dataLoading) {
  document.addEventListener('DOMContentLoaded', function () {
    setTimeout(() => {
      spinnerLoading.classList.add('not-visible');
      dataLoading.classList.remove('not-visible');
    }, 1000);
  });
}

var icon = document.getElementById('icon');
icon.onclick = function () {
  document.body.classList.toggle('darkmode');
  if (document.body.classList.contains('darkmode')) {
    // icon.src = "{% static 'img/sun.svg' %}";
    icon.src = '/static/img/sun.svg';
  } else {
    // icon.src = "{% static 'img/moon.svg' %}";
    icon.src = '/static/img/moon.svg';
  }
};

$(function () {
  $('[data-toggle="tooltip"]').tooltip();
});

setTimeout(function () {
  if ($('#msg').length > 0) {
    $('#msg').fadeOut();
  }
}, 2000);

// Only on the Login Page
if (document.getElementById('login-form')) {
  // Make submit button inactive until all fields are filled
  $(document).ready(function () {
    $('input[type="submit"]').prop('disabled', true);
    $('input[type="text"]').keyup(function () {
      if ($(this).val() != '' && $('input[type="password"]').val() != '') {
        $('input[type="submit"]').prop('disabled', false);
      }
    });
    $('input[type="password"]').keyup(function () {
      if ($(this).val() != '' && $('input[type="text"]').val() != '') {
        $('input[type="submit"]').prop('disabled', false);
      }
    });
  });
}

document.onkeyup = function (e) {
  if (e.ctrlKey && e.which == 67 && e.altKey) {
    // Redirect to create page
    window.location.href = '/create';
  }
};

$(document).ready(function () {
  $('input[id=passwordFirst]')
    .keyup(function () {
      var pswd = $(this).val();

      //validate the length
      if (pswd.length < 8) {
        $('#length').removeClass('valid').addClass('invalid');
      } else {
        $('#length').removeClass('invalid').addClass('valid');
      }

      //validate letter
      if (pswd.match(/[A-z]/)) {
        $('#letter').removeClass('invalid').addClass('valid');
      } else {
        $('#letter').removeClass('valid').addClass('invalid');
      }

      //validate capital letter
      if (pswd.match(/[A-Z]/)) {
        $('#capital').removeClass('invalid').addClass('valid');
      } else {
        $('#capital').removeClass('valid').addClass('invalid');
      }

      //validate number
      if (pswd.match(/\d/)) {
        $('#number').removeClass('invalid').addClass('valid');
      } else {
        $('#number').removeClass('valid').addClass('invalid');
      }

      //validate space
      if (pswd.match(/[^a-zA-Z0-9\-\/]/)) {
        $('#space').removeClass('invalid').addClass('valid');
      } else {
        $('#space').removeClass('valid').addClass('invalid');
      }
    })
    .focus(function () {
      $('#pswd_info').show();
    })
    .blur(function () {
      $('#pswd_info').hide();
    });
});

// Get the Stars
const first = document.getElementById('first');
const second = document.getElementById('second');
const third = document.getElementById('third');
const fourth = document.getElementById('fourth');
const fifth = document.getElementById('fifth');

const form = document.querySelector('.rate-form');
const confirmBox = document.getElementById('confirm-box');
const csrf = document.getElementsByName('csrfmiddlewaretoken');

const handleStarSelect = (size) => {
  const children = form.children;
  for (let i = 0; i < children.length; i++) {
    if (i <= size) {
      children[i].classList.add('checked');
    } else {
      children[i].classList.remove('checked');
    }
  }
};

const handleSelect = (selection) => {
  switch (selection) {
    case 'first':
      handleStarSelect(1);
      return;
    case 'second':
      handleStarSelect(2);
      return;
    case 'third':
      handleStarSelect(3);
      return;
    case 'fourth':
      handleStarSelect(4);
      return;
    case 'fifth':
      handleStarSelect(5);
      return;
  }
};

const getNumericValue = (stringValue) => {
  let numericValue;
  if (stringValue === 'first') {
    numericValue = 1;
  } else if (stringValue === 'second') {
    numericValue = 2;
  } else if (stringValue === 'third') {
    numericValue = 3;
  } else if (stringValue === 'fourth') {
    numericValue = 4;
  } else if (stringValue === 'fifth') {
    numericValue = 5;
  }
  return numericValue;
};

if (first) {
  const arr = [first, second, third, fourth, fifth];

  arr.forEach((item) => {
    item.addEventListener('mouseover', (event) => {
      handleSelect(event.target.id);
    });
  });

  arr.forEach((item) => {
    item.addEventListener('click', (event) => {
      const val = event.target.id;

      let isSubmit = false;

      form.addEventListener('submit', (e) => {
        e.preventDefault();
        if (isSubmit) {
          return;
        }
        isSubmit = true;
        const id = e.target.id;
        console.log(id);
        const val_num = getNumericValue(val);
        console.log(val_num);

        $.ajax({
          type: 'POST',
          url: '/rate_listing',
          data: {
            csrfmiddlewaretoken: csrf[0].value,
            listing_id: id,
            rating: val_num,
          },
          success: function (response) {
            console.log(response);
            // confirmBox.innerHTML = `<h1>Successfully rated with ${response.score}</h1>`;
          },
          error: function (error) {
            console.log(error);
            // confirmBox.innerHTML = `<h1>Failed to rate</h1>`;
          },
        });
      });
    });
  });
}

$('.custom-carousel').owlCarousel({
  autoWidth: true,
  loop: true,
  items: 5,
  itemsDesktop: [1000, 5], //5 items between 1000px and 901px
  itemsDesktopSmall: [900, 3], // betweem 900px and 601px
  itemsTablet: [600, 2], //2 items between 600 and 0;
  itemsMobile: false, // itemsMobile disabled - inherit from itemsTablet option
});
$(document).ready(function () {
  $('.custom-carousel .item').click(function () {
    $('.custom-carousel .item').not($(this)).removeClass('active');
    $(this).toggleClass('active');
  });
});


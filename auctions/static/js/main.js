const spinnerBox = document.getElementById('spinner-box');
const data = document.getElementById('data-box');

console.log(spinnerBox);
console.log(data);

$.ajax({
  type: 'GET',
  url: '/expenses',
  success: function (response) {
    setTimeout(() => {
      spinnerBox.classList.add('not-visible');
      data.classList.remove('not-visible');
    }, 500);
  },
  error: function (error) {
    setTimeout(() => {
      dataBox.innerHTML = '<b>Failed to load data</b>';
    }, 500);
  },
});

$(function () {
  $('[data-toggle="tooltip"]').tooltip();
});

setTimeout(function () {
  if ($('#msg').length > 0) {
    $('#msg').fadeOut();
  }
}, 2000);

// TODO - Make this specific to login page only
// Make submit button inactive until all fields are filled
// $(document).ready(function () {
//   $('input[type="submit"]').prop('disabled', true);
//   $('input[type="text"]').keyup(function () {
//     if ($(this).val() != '' && $('input[type="password"]').val() != '') {
//       $('input[type="submit"]').prop('disabled', false);
//     }
//   });
//   $('input[type="password"]').keyup(function () {
//     if ($(this).val() != '' && $('input[type="text"]').val() != '') {
//       $('input[type="submit"]').prop('disabled', false);
//     }
//   });
// });

document.onkeyup = function (e) {
  if (e.ctrlKey && e.which == 67 && e.altKey) {
    window.location.href = "{% url 'create' %}";
    // alert("Ctrl + B shortcut combination was pressed");
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

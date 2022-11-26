document.addEventListener('DOMContentLoaded', function () {
  preloader = document.querySelector('#preloader');
  email_content = document.querySelector('#email_content');
  footer_content = document.querySelector('#footer_content');
  mail_image = document.querySelector('#mail_image');

  setTimeout(() => {
    preloader.classList.add('not-visible');
    email_content.classList.remove('not-visible');
    footer_content.classList.remove('not-visible');
    mail_image.classList.remove('not-visible');
  }, 2000);

  // Use buttons to toggle between views
  document
    .querySelector('#inbox')
    .addEventListener('click', () => load_mailbox('inbox'));
  document
    .querySelector('#sent')
    .addEventListener('click', () => load_mailbox('sent'));
  document
    .querySelector('#archived')
    .addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  // By default, load the inbox
  localStorage.clear();
  load_mailbox('inbox');

  // Send email when compose form submitted
  document.querySelector('form').onsubmit = send_email;
});

// compose_email(email.sender, email.recipients, email.subject, email.body);
// "On Jan 1 2020, 12:00 AM foo@example.com wrote:"
function compose_email(email, reply) {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#single_email_view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  if (reply) {
    document.querySelector('#compose-recipients').disabled = true;
    document.querySelector('#compose-recipients').value = email.sender;
    if (email.subject.substring(0, 3) === 'Re:')
      document.querySelector('#compose-subject').value = email.subject;
    else {
      document.querySelector('#compose-subject').value = 'Re: ' + email.subject;
    }
    document.querySelector('#compose-body').innerHTML =
      '\r\n' +
      '\r\n' +
      `>>>On ${email.timestamp} ${email.sender} wrote: ` +
      '\r\n' +
      '\r\n' +
      email.body;
  } else {
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
  }
}

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#single_email_view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${
    mailbox.charAt(0).toUpperCase() + mailbox.slice(1)
  }</h3>`;

  // if (mailbox === 'sent') {
  show_mail(mailbox);
  // }
}

function send_email() {
  recipients_compose = document.querySelector('#compose-recipients').value;
  subject_compose = document.querySelector('#compose-subject').value;
  body_compose = document.querySelector('#compose-body').value;

  fetch('mail/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients_compose,
      subject: subject_compose,
      body: body_compose,
    }),
  })
    .then((response) => response.json())
    .then((result) => {
      // Print result
      if (result.message === 'Email sent successfully.') {
        localStorage.clear();
        load_mailbox('sent');
      } else {
        const div = document.createElement('div');
        div.className = 'alert alert-danger';
        div.role = 'alert';
        div.innerHTML =
          'Error! Unable to send message to ' +
          recipients_compose +
          '. Email does not exist!';
        document.querySelector('#compose-view').append(div);
      }
    });

  return false;
}

function show_mail(mailbox) {
  console.log('mail/emails/' + mailbox);

  fetch('mail/emails/' + mailbox)
    .then((response) => response.json())
    .then((emails) => {
      // Print emails
      console.log(emails);

      emails.forEach((email) => {
        var prefix = mailbox === 'inbox' ? 'From: ' : 'To: ';
        const div = document.createElement('div');
        const subject = document.createElement('div');
        const time = document.createElement('div');
        const from_to = document.createElement('div');

        if (mailbox === 'inbox') {
          from_to.innerHTML = prefix + email.sender;
        } else {
          from_to.innerHTML = prefix + email.recipients;
        }

        subject.innerHTML = email.subject;
        time.innerHTML = email.timestamp;
        time.className = 'time';
        subject.className = 'subject';

        div.append(from_to);
        div.append(subject);
        div.append(time);
        div.setAttribute('id', email.id);

        if (email.read) {
          div.className += 'email read';
        } else {
          div.className += 'email';
        }

        div.addEventListener('click', function () {
          one_email(email.id);
        });

        document.querySelector('#emails-view').append(div);
      });
    });
}

function one_email(id) {
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#single_email_view').style.display = 'block';

  console.log('Email ID: ' + id + ' has been clicked.');

  fetch(`mail/emails/${id}`)
    .then((response) => response.json())
    .then((email) => {
      update_read(id);
      const subject = document.querySelector('#subject');
      const from = document.querySelector('.from');
      const to = document.querySelector('.to');
      const body = document.querySelector('#body');
      const timestamp = document.querySelector('#timestamp');
      subject.innerHTML = email.subject;
      from.innerHTML = email.sender;
      to.innerHTML = email.recipients;
      body.innerHTML = email.body;
      // Convert time to PST time
      timestamp.innerHTML = '⏰ ' + email.timestamp + ' PST';

      const reply = document.createElement('button');
      reply.className = 'btn btn-success btn-sm right_align reply rounded-pill';
      const reply_icon = document.createElement('i');
      reply_icon.className = 'fa-solid fa-reply';
      reply_icon.textContent = ' Reply';
      reply.append(reply_icon);
      from.append(reply);

      const archive = document.createElement('button');
      archive.className =
        'btn btn-warning btn-sm right_align archive rounded-pill';
      const archive_icon = document.createElement('i');
      archive_icon.className = 'fa-solid fa-box-archive';
      if (email.archived) {
        archive_icon.textContent = ' Un-Archive';
      } else {
        archive_icon.textContent = ' Archive';
      }
      archive.append(archive_icon);

      archive.addEventListener('click', function () {
        if (email.archived) {
          console.log(`updating email ${email.id} as archived = false`);
          archive_mail(id, false);
        } else {
          console.log(`updating email ${email.id} as archived = true`);
          archive_mail(id, true);
        }
      });
      to.append(archive);

      reply.addEventListener('click', function () {
        compose_email(email, true);
      });
    });
}

function archive_mail(id, state) {
  fetch(`mail/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: state,
    }),
  });
  localStorage.clear();
  load_mailbox('inbox');
}

function update_read(id) {
  console.log(`updating email ${id} as read = true`);
  fetch(`mail/emails/${id}`, {
    method: 'PUT',
    body: (body = JSON.stringify({
      read: true,
    })),
  });
}

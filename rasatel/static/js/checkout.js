

async function postData(url = '', data) {
  console.log(JSON.stringify(data))
  // Default options are marked with *
  const response = await fetch(url, {
    method: 'POST', // *GET, POST, PUT, DELETE, etc.
    mode: 'cors', // no-cors, *cors, same-origin
    cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
    credentials: 'same-origin', // include, *same-origin, omit
    headers: {

      'X-CSRFToken': csrftoken,
      // 'Content-Type': 'application/x-www-form-urlencoded',
    },
    redirect: 'follow', // manual, *follow, error
    referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url

    body: JSON.stringify(data) // body data type must match "Content-Type" header
  });
  return response.json(); // parses JSON response into native JavaScript objects
}


const stripe = Stripe('pk_test_51IqiplGO3c1oiuNYczIlzKFh6uqylOdEHWLTuuTPirRZ7U6CEggQQAMGjlgVc51PWZTRcN7MWZblhEAtgLT5jgoI00vT0AiTl0');
const paymentFormSecretId = document.getElementById("payment-form");
const options = {
  clientSecret: paymentFormSecretId.dataset.secret,
  // Fully customizable with appearance API.
};

// Set up Stripe.js and Elements to use in checkout form, passing the client secret obtained in step 2
const elements2 = stripe.elements(options);

// Create and mount the Payment Element
const paymentElement = elements2.create('payment');
paymentElement.mount('#payment-element');

const form = document.getElementById('payment-form');

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  var data = {};
  const formData = new FormData(form);
  for (var [key, value] of formData.entries()) {
    data[key] = value
  }
  data['stripeId']=paymentFormSecretId.dataset.secret


  postData('http://192.168.81.130/checkout/' + planId, data)
    .then(data => {
      if (data['status'] == 1) {
        const { error } = stripe.confirmSetup({
          //`Elements` instance that was used to create the Payment Element
          elements: elements2,
          confirmParams: {
            return_url: 'http://192.168.81.130/checkout/paymentcomplete?confirmId='+data['id'],
          }
        });

        if (error) {
          // This point will only be reached if there is an immediate error when
          // confirming the payment. Show error to your customer (e.g., payment
          // details incomplete)
          const messageContainer = document.querySelector('#error-message');
          messageContainer.textContent = error.message;
        } else {
        }
      }
    });
});
const api = 'https://api.openweathermap.org/data/2.5/weather';
const apiKey = 'YOUR_API_KEY';
const searchButton = document.getElementById('search');
searchButton.addEventListener('click', async () => {
  const city = document.getElementById('city').value;
  const resp = await fetch(`${api}?q=${city}&appid=${apiKey}&units=metric`);
  const data = await resp.json();
  document.getElementById('weather').innerHTML = `The weather in ${city} is ${data.weather[0].description}`;
  document.getElementById('description').innerHTML = `Description: ${data.weather[0].description}`;
  document.getElementById('temperature').innerHTML = `Temperature: ${data.main.temp}°C`;
  document.getElementById('humidity').innerHTML = `Humidity: ${data.main.humidity}%`;
  document.getElementById('wind').innerHTML = `Wind: ${data.wind.speed} m/s`;
});
console.log('Script loaded');
console.log('Waiting for user input');
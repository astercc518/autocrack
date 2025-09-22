import App from './App';

const root = document.getElementById('root');
if (root) {
  root.innerHTML = '<h1>' + App() + '</h1>';
}
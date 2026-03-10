<h1 align="center">🎵 Sonic 🎵</h1>

<p align="center">
  <img src="https://files.catbox.moe/bhdbfj.jpeg" alt="Sonic Logo">
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/urstark/Sonic?style=for-the-badge&color=blue" alt="GitHub stars">
  <img src="https://img.shields.io/github/forks/urstark/Sonic?style=for-the-badge&color=blue" alt="GitHub forks">
  <img src="https://img.shields.io/github/issues/urstark/Sonic?style=for-the-badge&color=red" alt="GitHub issues">
  <img src="https://img.shields.io/github/license/urstark/Sonic?style=for-the-badge&color=green" alt="GitHub license">
</p>

<h2 align="center">Delivering Superior Music Experience to Telegram</h2>

---

### 🛠 Fix for YouTube Blocking VPS IPs

YouTube blocks many VPS IPs. We now provide **two ways** to keep playback smooth:

1. **API (Recommended):**  
   Stream **audio & video** via our API with built-in vPlay support. No cookie hassle.

2. **Custom Cookies (Fallback / No-API mode):**  
   Generate cookies on your local machine and place them in the `cookies/` folder to bypass YouTube restrictions.

---

## 🎵 Using the API for Audio & Video (vPlay)

The API now supports **both audio and video**.  
Use API for reliability; switch to **custom cookies** if you prefer not to rely on the API.

---

### 🔑 Get an API Key

Manage keys from our official dashboard (no Telegram DMs needed):

[![API Dashboard](https://img.shields.io/badge/Visit-Dashboard-black?style=for-the-badge&logo=vercel)](http://sonichub.vercel.app)  
[![API Community](https://img.shields.io/badge/Join-API%20Community-green?style=for-the-badge&logo=telegram)](https://t.me/SonicsHub)  
[![Contact Stark](https://img.shields.io/badge/DM-@urstarkz-blueviolet?style=for-the-badge&logo=telegram)](https://t.me/urstarkz)  

---

#### 🛠️ Steps to Get Started

1. **Sign up** at [sonichub.vercel.app](https://sonichub.vercel.app) and create an account.  
2. **Generate Key**: After logging in, click **“Generate Key”** on the dashboard to activate the **Free Plan**.  
3. **Upgrade anytime** via the dashboard or contacting [@urSTARKz](https://t.me/urstarkz)  on telegram for higher limits.  

---

### 📌 Important Notes About API Usage

- 🔄 **Daily Reset**: All limits reset at every hour (IST).  
- 🎧🎬 **Audio + Video**: Fully supported via API (vPlay).  
- 🍪 **Fallback**: Add local **custom cookies** if you prefer not to use the API (works for both audio & video).  
- 💬 **Support**: Join the [API Community Group](https://t.me/SonicsHub).  

---

### ⚙️ Integration

Add your API key to `.env`:


API_KEY=your-api-key-here

---

### 🌟 Features

- 🎵 **Multiple Sources:** Play music from various platforms.
- 📃 **Queue System:** Line up your favorite songs.
- 🔀 **Advanced Controls:** Shuffle, repeat, and more.
- 🎛 **Customizable Settings:** From equalizer to normalization.
- 📢 **Crystal Clear Audio:** High-quality playback.
- 🎚 **Volume Mastery:** Adjust to your preferred loudness.

---

## 🚀 Deploy on Heroku 
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://dashboard.heroku.com/new?template=https://github.com/urstark/Sonic)

---

### 🔧 Quick Setup

1. **Upgrade & Update:**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

2. **Install Required Packages:**
   ```bash
   sudo apt-get install python3-pip ffmpeg -y
   ```
3. **Setting up PIP**
   ```bash
   sudo pip3 install -U pip
   ```
4. **Clone the Repository**
   ```bash
   git clone https://github.com/urstark/Sonic && cd Sonic
   ```
5. **Install Requirements**
   ```bash
   pip3 install -U -r requirements.txt
   ```
6. **Create .env  with sample.env**
   ```bash
   cp sample.env .env
   ```
   - Edit .env with your vars
7. **Editing Vars:**
   ```bash
   vi .env
   ```
   - Edit .env with your values.
   - Press `I` button on keyboard to start editing.
   - Press `Ctrl + C`  once you are done with editing vars and type `:wq` to save .env or `:qa` to exit editing.
8. **Installing tmux**
    ```bash
    sudo apt install tmux -y && tmux
    ```
9. **Run the Bot**
    ```bash
    bash start
    ```

---

### 🛠 Commands & Usage

The Sonic Music Bot offers a range of commands to enhance your music listening experience on Telegram:

| Command                 | Description                                 |
|-------------------------|---------------------------------------------|
| `/play <song name>`     | Play the requested song.                    |
| `/pause`                | Pause the currently playing song.           |
| `/resume`               | Resume the paused song.                     |
| `/skip`                 | Move to the next song in the queue.         |
| `/stop`                 | Stop the bot and clear the queue.           |
| `/queue`                | Display the list of songs in the queue.     |

For a full list of commands, use `/help` in [telegram](https://t.me/SanyaxMusicBot).

---

### 🔄 Updates & Support

Stay updated with the latest features and improvements to Sonic Music Bot:

<p align="center">
  <a href="https://telegram.me/SonicsHub">
    <img src="https://img.shields.io/badge/Join-Update%20Channel-blue?style=for-the-badge&logo=telegram">
  </a>
</p>

---

### 🤝 Contributing

We welcome contributions to the Sonic project. If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch with a meaningful name.
3. Make your changes and commit them with a descriptive commit message.
4. Open a pull request against our `main` branch.
5. Our team will review your changes and provide feedback.

For more details, reach out us on telegram.

---

### 📜 License

This project is licensed under the MIT License. For more details, see the [LICENSE](LICENSE) file.

---

### 🙏 Acknowledgements

Thanks to all the contributors, supporters, and users of the Sonic Music Bot. Your feedback and support keep us going!
- Yukki Music & AnonX Music – Base inspiration
- All contributors & community members
  
---

⭐ If you like this project, don’t forget to star the repo!


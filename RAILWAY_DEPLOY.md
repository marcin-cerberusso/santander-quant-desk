# 🚀 RAILWAY DEPLOYMENT GUIDE

## Krok po kroku: Wdrożenie Santander Quant Desk na Railway

### 📋 Przygotowania (GOTOWE ✅)

Wszystkie pliki są już przygotowane:
- ✅ `dashboard.py` - Główna aplikacja
- ✅ `requirements.txt` - Zależności Python
- ✅ `.streamlit/config.toml` - Konfiguracja dla Railway
- ✅ `.gitignore` - Wykluczenia Git
- ✅ `README.md` - Dokumentacja
- ✅ Git repository zainicjalizowane

---

### 🌐 Deployment na Railway (5 minut)

#### Opcja A: Deploy z GitHuba (REKOMENDOWANE)

1. **Utwórz repozytorium na GitHubie**
   ```bash
   # W przeglądarce, idź na github.com
   # Kliknij "New repository"
   # Nazwa: "santander-quant-desk"
   # Public lub Private (twój wybór)
   # NIE zaznaczaj "Initialize with README" (mamy już)
   ```

2. **Podłącz lokalne repo do GitHuba**
   ```bash
   cd /home/marcin/Downloads/CopyW
   git remote add origin https://github.com/TWOJ_USERNAME/santander-quant-desk.git
   git branch -M main
   git push -u origin main
   ```

3. **Deploy na Railway**
   - Idź na [railway.app](https://railway.app)
   - Kliknij "Start a New Project"
   - Wybierz "Deploy from GitHub repo"
   - Autoryzuj Railway do GitHuba
   - Wybierz repo `santander-quant-desk`
   - Railway **automatycznie wykryje Streamlit** i zdeployuje

4. **Konfiguracja (automatyczna)**
   - Railway wykryje `requirements.txt`
   - Zainstaluje wszystkie zależności
   - Uruchomi `streamlit run dashboard.py`
   - Przydzieli publiczny URL (np. `https://santander-quant-desk.up.railway.app`)

5. **Gotowe! 🎉**
   - Aplikacja dostępna pod Railway URL
   - Auto-redeploy po każdym `git push`
   - Darmowy plan: 500h/miesiąc (wystarczy na hobby projekt)

---

#### Opcja B: Deploy bez GitHuba (Railway CLI)

```bash
# Zainstaluj Railway CLI
npm i -g @railway/cli

# Zaloguj się
railway login

# Zainicjuj projekt
railway init

# Deploy
railway up

# Otwórz w przeglądarce
railway open
```

---

### 🔧 Zaawansowana konfiguracja (Opcjonalne)

#### Custom Domain
1. W Railway Dashboard → Settings
2. "Generate Domain" lub "Add Custom Domain"
3. Jeśli custom: dodaj CNAME w DNS providera

#### Environment Variables (jeśli kiedyś dodamy API keys)
1. Railway Dashboard → Variables
2. Dodaj `API_KEY=xxx`
3. W `dashboard.py` użyj `os.getenv('API_KEY')`

#### Monitoring
- Railway Dashboard pokazuje:
  - CPU usage
  - Memory usage  
  - Request logs
  - Deployment history

---

### 💰 Koszty

**Free Plan:**
- 500h runtime/miesiąc
- $5 credit/miesiąc (wystarczy dla małego ruchu)
- Automatyczne usypianie po 30 min bezczynności

**Hobby Plan ($5/m):**
- Unlimited hours
- Priority support
- Custom domains

Dla tego projektu: **Free plan wystarczy** (aplikacja jest lekka, używa tylko yfinance API).

---

### 📊 Po deploymencie

Twoja aplikacja będzie dostępna 24/7 pod Railway URL. Możesz:
- Udostępnić link znajomym/inwestorom
- Dodać do portfolio
- Używać z telefonu/tabletu
- Automatyczne aktualizacje po `git push`

---

### 🐛 Troubleshooting

**Problem: "Application failed to start"**
→ Sprawdź logi w Railway Dashboard. Prawdopodobnie brak zależności w `requirements.txt`.

**Problem: "Port binding error"**
→ Streamlit automatycznie używa $PORT z Railway. Config już to obsługuje.

**Problem: "Memory limit exceeded"**
→ yfinance pobiera dużo danych. Zmniejsz liczbę tickerów w `TICKERS` lub przejdź na Hobby Plan.

**Problem: "API rate limit"**
→ yfinance ma limity. Dodaj `time.sleep()` między requestami lub użyj cache (już mamy `@st.cache_data(ttl=60)`).

---

### 🎯 Next Steps

1. **Deploy** (5 min)
2. **Testuj** na Railway URL
3. **Share** z innymi traderami
4. **Iterate** - dodawaj nowe features (ML predictions, alerts, backtesting)

---

**Gotowy do wypuszczenia w świat?** 🚀

Jeśli masz już konto GitHub, wystarczy 3 komendy:
```bash
git remote add origin https://github.com/USERNAME/santander-quant-desk.git
git push -u origin main
# Potem Railway → Deploy from GitHub
```

**Powodzenia!** 💪📈

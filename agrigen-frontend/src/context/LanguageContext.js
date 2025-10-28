import React, { createContext, useState, useEffect } from "react";

export const LanguageContext = createContext();

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState("en");

  // Load language preference from localStorage
  useEffect(() => {
    const storedLanguage = localStorage.getItem("agrigenai_language");
    if (storedLanguage) {
      setLanguage(storedLanguage);
    }
  }, []);

  // Save language preference to localStorage
  useEffect(() => {
    localStorage.setItem("agrigenai_language", language);
  }, [language]);

  // Translations object (expandable for future)
  const translations = {
    en: {
      // English translations
      welcome: "Welcome",
      login: "Login",
      signup: "Sign Up",
      logout: "Logout",
      analyze: "Analyze",
      cart: "Cart",
      profile: "Profile",
      // Add more translations as needed
    },
    hi: {
      // Hindi translations (future)
      welcome: "स्वागत है",
      login: "लॉगिन",
      signup: "साइन अप करें",
      logout: "लॉगआउट",
      analyze: "विश्लेषण करें",
      cart: "कार्ट",
      profile: "प्रोफ़ाइल",
    },
    kn: {
      // Kannada translations (future)
      welcome: "ಸ್ವಾಗತ",
      login: "ಲಾಗಿನ್",
      signup: "ಸೈನ್ ಅಪ್",
      logout: "ಲಾಗೌಟ್",
      analyze: "ವಿಶ್ಲೇಷಣೆ",
      cart: "ಕಾರ್ಟ್",
      profile: "ಪ್ರೊಫೈಲ್",
    },
    ta: {
      // Tamil translations (future)
      welcome: "வரவேற்பு",
      login: "உள்நுழைய",
      signup: "பதிவு செய்க",
      logout: "வெளியேறு",
      analyze: "பகுப்பாய்வு",
      cart: "வண்டி",
      profile: "சுயவிவரம்",
    },
    te: {
      // Telugu translations (future)
      welcome: "స్వాగతం",
      login: "లాగిన్",
      signup: "సైన్ అప్",
      logout: "లాగౌట్",
      analyze: "విశ్లేషణ",
      cart: "కార్ట్",
      profile: "ప్రొఫైల్",
    },
  };

  // Get translated text
  const t = (key) => {
    return translations[language]?.[key] || translations.en[key] || key;
  };

  // Change language
  const changeLanguage = (newLanguage) => {
    if (translations[newLanguage]) {
      setLanguage(newLanguage);
    }
  };

  const value = {
    language,
    setLanguage: changeLanguage,
    t,
    availableLanguages: [
      { code: "en", name: "English", flag: "🇬🇧", enabled: true },
      { code: "hi", name: "हिंदी", flag: "🇮🇳", enabled: false },
      { code: "kn", name: "ಕನ್ನಡ", flag: "🇮🇳", enabled: false },
      { code: "ta", name: "தமிழ்", flag: "🇮🇳", enabled: false },
      { code: "te", name: "తెలుగు", flag: "🇮🇳", enabled: false },
    ],
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

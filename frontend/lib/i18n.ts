export const translations = {
  en: {
    onboarding: {
      title: "GramNirnay.ai",
      subtitle: "Conversational Onboarding",
      send: "Send",
      analyzing: "Analyzing your profile...",
      voice_input: "Use voice input",
      step1_title: "The Idea",
      step1_desc: "Tell us what you're planning to build.",
      step2_title: "Available Capital",
      step2_desc: "How much seed money do you have?",
      step3_title: "Target Investment",
      step3_desc: "What's the total cost of the project?",
      step4_title: "Experience",
      step4_desc: "Your background in this industry.",
      step5_title: "District",
      step5_desc: "Where is your business located?",
      step6_title: "State",
      step6_desc: "Which state are you in?"
    },
    report: {
      title: "Analysis Report",
      subtitle: "Hyper-Local Business Intelligence",
      new_analysis: "Start New Analysis",
      sandbox_title: "Financial Sandbox",
      sandbox_subtitle: "Tweak parameters to see real-time viability",
      viability_score: "Viability Score",
      ai_insights: "AI Insights",
      context_reasoning: "Contextual Reasoning",
      roadmap_title: "Financing Roadmap"
    }
  },
  hi: {
    onboarding: {
      title: "ग्रामनिर्णय AI",
      subtitle: "संवादात्मक ऑनबोर्डिंग",
      send: "भेजें",
      analyzing: "आपके प्रोफाइल का विश्लेषण किया जा रहा है...",
      voice_input: "आवाज का उपयोग करें",
      step1_title: "विचार",
      step1_desc: "हमें बताएं कि आप क्या बनाने की योजना बना रहे हैं।",
      step2_title: "उपलब्ध पूंजी",
      step2_desc: "आपके पास कितना बीज धन है?",
      step3_title: "लक्ष्य निवेश",
      step3_desc: "परियोजना की कुल लागत क्या है?",
      step4_title: "अनुभव",
      step4_desc: "इस उद्योग में आपकी पृष्ठभूमि।",
      step5_title: "जिला",
      step5_desc: "आपका व्यवसाय कहाँ स्थित है?",
      step6_title: "राज्य",
      step6_desc: "आप किस राज्य में हैं?"
    },
    report: {
      title: "विश्लेषण रिपोर्ट",
      subtitle: "हाइपर-लोकल बिजनेस इंटेलिजेंस",
      new_analysis: "नया विश्लेषण शुरू करें",
      sandbox_title: "वित्तीय सैंडबॉक्स",
      sandbox_subtitle: "वास्तविक समय में व्यवहार्यता देखने के लिए मापदंडों को बदलें",
      viability_score: "व्यवहार्यता स्कोर",
      ai_insights: "AI अंतर्दृष्टि",
      context_reasoning: "संदर्भ तर्क",
      roadmap_title: "वित्तपोषण रोडमैप"
    }
  }
};

export type Language = 'en' | 'hi';

export function t(lang: Language, path: string): string {
  const keys = path.split('.');
  let result: Record<string, unknown> = translations[lang] as Record<string, unknown>;
  for (const key of keys) {
    if (result[key] === undefined) return path;
    result = result[key] as Record<string, unknown>;
  }
  return result as unknown as string;
}

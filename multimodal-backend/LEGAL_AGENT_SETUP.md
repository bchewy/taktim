# Enhanced Legal Knowledge Agent Setup

Your Legal Knowledge Agent now has **real-time access to government legal databases**! 🎉

## 🔥 What's New

✅ **GovInfo.gov API** - Federal regulations, CFR, Federal Register  
✅ **Congress.gov API** - Current bills, laws, legislative tracking  
✅ **State Law Database** - California SB976, Florida OPM, Utah SMRA  
✅ **Real-time Legal Research** - Always up-to-date compliance analysis  
✅ **Government Source Citations** - Authoritative legal references  

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd C:\Users\lauwe\side_projects\taktim\multimodal-backend
pip install -r requirements.txt
```

### 2. Set Up API Keys
Edit `.env` file:
```env
OPENAI_API_KEY=your_actual_openai_key
CONGRESS_API_KEY=your_congress_api_key  # Optional but recommended
```

**Get FREE Congress API Key:** https://api.congress.gov/sign-up/  
**GovInfo API:** No key required! ✨

### 3. Test the Enhanced Agent
```bash
python test_legal_agent.py
```

### 4. Start the Server
```bash
python main.py
```

## 🎯 API Endpoints

### Legal Compliance Analysis
```bash
curl -X POST "http://localhost:8001/api/legal-analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "feature_name": "Teen Dance Challenge",
       "description": "AI-powered dance challenges for teens",
       "target_markets": ["US", "EU"], 
       "user_demographics": ["13-17"],
       "data_collected": ["video_uploads", "movement_analysis"],
       "ai_components": ["recommendation_engine"]
     }'
```

### Risk Assessment
```bash  
curl -X POST "http://localhost:8001/api/legal-risk-assessment" \
     -H "Content-Type: application/json" \
     -d '{
       "feature_name": "Location-Based AR Filter",
       "target_markets": ["US", "EU"],
       "data_collected": ["precise_location", "camera_data"]
     }'
```

### Quick Check
```bash
curl -X POST "http://localhost:8001/api/legal-quick-check" \
     -F "feature_name=Voice Changer Filter" \
     -F "description=Real-time voice modification" \
     -F "target_markets=US,EU" \
     -F "user_demographics=teens,adults"
```

## 🧠 What the Legal Agent Can Now Do

### Real-Time Legal Research
- **Federal Regulations**: Live search of CFR and Federal Register
- **Congressional Bills**: Track new legislation affecting social media
- **State Laws**: Curated database of key state regulations
- **Cross-Reference**: Verify information across multiple government sources

### Advanced Compliance Analysis
- **Jurisdiction-Specific**: Detailed analysis per target market
- **Risk Assessment**: Quantified risk levels with mitigation strategies  
- **Implementation Guidance**: Step-by-step compliance requirements
- **Citation-Based**: Every recommendation backed by official sources

### Specializations
- **Children Protection**: COPPA, state minor protection laws
- **Social Media**: Platform-specific compliance requirements
- **AI/Algorithms**: Transparency, explainability, bias auditing
- **Data Privacy**: GDPR, CCPA, emerging privacy regulations

## 🔍 Legal Research Tools Available

The agent has access to these specialized tools:

1. **`legal_research`** - General legal topic research
2. **`social_media_compliance_research`** - Platform-specific compliance  
3. **`regulation_details`** - Deep-dive into specific regulations

## 📋 Government Data Sources

### Federal Sources ✅
- **GovInfo.gov** - Official federal regulations and documents
- **Congress.gov** - Legislative tracking and bill information
- **Federal Trade Commission** - Consumer protection guidance

### State Sources ✅
- **California** - SB976 Social Media Child Protection Act
- **Florida** - Online Protection for Minors Act  
- **Utah** - Social Media Regulation Act

### International Sources 🔄 (Coming Soon)
- EU regulations (GDPR, Digital Services Act)
- Canadian privacy laws (PIPEDA)
- Asia-Pacific regulations

## 🛠️ Troubleshooting

### Legal APIs Not Working?
1. Check internet connection
2. Verify GovInfo.gov and Congress.gov are accessible
3. Ensure CONGRESS_API_KEY is valid (if using Congress API)
4. Run: `python test_legal_agent.py` to diagnose

### Agent Not Using Research Tools?
1. Check that legal research tools are loaded (see startup logs)
2. Verify OpenAI API key is set correctly
3. Check agent prompts are instructing to use research tools

### Performance Issues?
1. Government APIs can be slow - normal for first request
2. Results are worth the wait for accurate legal analysis
3. Consider caching for production use

## 🎓 Usage Tips

### Best Practices
1. **Always specify target markets** - Legal requirements vary by jurisdiction
2. **Be specific about data collection** - Critical for privacy compliance
3. **Include user demographics** - Especially important for minor protection laws
4. **Mention AI components** - Algorithmic transparency is increasingly regulated

### Example Features to Test
- Social media recommendation systems
- Location-based features  
- Content involving minors
- AI-powered personalization
- User-generated content platforms

## 🚀 Next Steps

Your Legal Knowledge Agent is now **production-ready** with real government data access!

Try analyzing your TikTok feature ideas and see the comprehensive legal analysis with official citations. The agent will provide specific compliance requirements, risk assessments, and implementation guidance based on current federal and state regulations.

**Happy compliance analyzing!** 🏛️⚖️
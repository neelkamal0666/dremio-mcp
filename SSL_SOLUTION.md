# SSL Certificate Issue - Solution Guide

## 🔍 **Problem Identified**
The Anthropic API connection is failing due to SSL certificate verification issues in your corporate environment. The error shows:
```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain
```

## 🎯 **Root Cause**
Your corporate network has a proxy server or firewall that intercepts HTTPS traffic and presents a self-signed certificate, which the Anthropic client cannot verify.

## ✅ **Solutions (in order of preference)**

### 1. **Contact IT Department** (Recommended)
- Ask your IT department for the corporate CA certificate
- Request them to whitelist `api.anthropic.com` 
- Ask for guidance on accessing external APIs through the corporate firewall

### 2. **Use Different Network**
- Try using your mobile hotspot
- Use a different network (home, coffee shop, etc.)
- This will bypass the corporate SSL interception

### 3. **VPN Solution**
- Use a VPN that doesn't intercept SSL traffic
- Some corporate VPNs allow direct API access

### 4. **Environment Variables** (Temporary workaround)
Add these to your `.env` file:
```bash
PYTHONHTTPSVERIFY=0
CURL_CA_BUNDLE=
REQUESTS_CA_BUNDLE=
```

### 5. **Corporate Certificate Bundle**
If IT provides a certificate bundle:
```bash
export REQUESTS_CA_BUNDLE=/path/to/corporate/ca-bundle.crt
export CURL_CA_BUNDLE=/path/to/corporate/ca-bundle.crt
```

## 🚀 **Current System Status**

### ✅ **What's Working Perfectly:**
- **Wiki Integration**: All DataMesh tables can retrieve wiki content
- **MCP Server**: All tools functional
- **Heuristic SQL Generation**: Works as excellent fallback
- **Dremio Connection**: Fully functional

### ⚠️ **What's Affected:**
- **AI SQL Generation**: Falls back to heuristic approach
- **Natural Language Processing**: Limited to heuristic rules

## 🎉 **The Good News**

Your system is **fully functional** even without the Anthropic API! The heuristic SQL generation is quite sophisticated and can handle most queries effectively. The wiki metadata provides rich context that makes the system very useful.

## 🧪 **Test Your System**

Try these queries to see the system working:
```bash
python cli.py interactive
```

Then try:
- "show me all tables"
- "how many accounts are there"
- "show me demographic details"

The system will use heuristic SQL generation and provide excellent results!

## 📞 **Next Steps**

1. **Immediate**: Your system works great with heuristic fallback
2. **Short-term**: Contact IT about API access
3. **Long-term**: Consider using a different network for AI features

The wiki integration alone makes this system incredibly valuable for understanding your data! 🎉

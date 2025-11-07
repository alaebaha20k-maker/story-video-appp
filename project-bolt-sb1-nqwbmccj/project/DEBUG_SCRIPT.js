/**
 * AI Video Generator - Browser Debug Script
 *
 * Paste this entire script into the browser console (F12) to diagnose connection issues
 *
 * Instructions:
 * 1. Open DevTools (F12)
 * 2. Go to Console tab
 * 3. Paste this entire script
 * 4. Press Enter
 * 5. Follow the output
 */

console.log('%c=== AI Video Generator - Diagnostic Test ===', 'font-size: 16px; font-weight: bold; color: #6366f1;');

const API_BASE_URL = 'http://localhost:5000';

async function runDiagnostics() {
  console.log('\n📋 Starting diagnostics...\n');

  // Test 1: Check if API is reachable
  console.log('1️⃣  Testing API Health...');
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (response.ok) {
      const data = await response.json();
      console.log('%c✅ API is reachable!', 'color: green; font-weight: bold;');
      console.log('   Response:', data);
    } else {
      console.log('%c❌ API returned error status', 'color: red; font-weight: bold;');
      console.log('   Status:', response.status, response.statusText);
    }
  } catch (error) {
    console.log('%c❌ Cannot reach API', 'color: red; font-weight: bold;');
    console.log('   Error:', error.message);
    console.log('\n   Possible issues:');
    console.log('   - Backend is not running at http://localhost:5000');
    console.log('   - Backend port is different');
    console.log('   - Firewall is blocking connections');
  }

  // Test 2: Check CORS
  console.log('\n2️⃣  Testing CORS Headers...');
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Origin': window.location.origin
      }
    });
    const corsHeader = response.headers.get('Access-Control-Allow-Origin');

    if (corsHeader) {
      console.log('%c✅ CORS is properly configured', 'color: green; font-weight: bold;');
      console.log('   Access-Control-Allow-Origin:', corsHeader);
    } else {
      console.log('%c⚠️  CORS headers not present', 'color: orange; font-weight: bold;');
      console.log('   Your backend may not have CORS enabled');
      console.log('\n   Fix this by adding to your Flask app:');
      console.log('   from flask_cors import CORS');
      console.log('   CORS(app)');
    }
  } catch (error) {
    console.log('%c❌ Cannot test CORS', 'color: red; font-weight: bold;');
    console.log('   Error:', error.message);
  }

  // Test 3: Check POST endpoint
  console.log('\n3️⃣  Testing POST /api/generate-video...');
  try {
    const response = await fetch(`${API_BASE_URL}/api/generate-video`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        topic: 'Test',
        story_type: 'scary_horror',
        image_style: 'cinematic',
        image_mode: 'ai_only',
        voice_id: 'male_narrator_deep',
        duration: 5
      })
    });

    if (response.ok) {
      const data = await response.json();
      console.log('%c✅ POST endpoint is working', 'color: green; font-weight: bold;');
      console.log('   Response:', data);
    } else {
      console.log('%c⚠️  POST endpoint returned error', 'color: orange; font-weight: bold;');
      console.log('   Status:', response.status, response.statusText);
      const text = await response.text();
      console.log('   Response:', text);
    }
  } catch (error) {
    console.log('%c❌ POST endpoint error', 'color: red; font-weight: bold;');
    console.log('   Error:', error.message);
    if (error.message.includes('Failed to fetch')) {
      console.log('\n   This typically means:');
      console.log('   - Backend is not running');
      console.log('   - Port 5000 is not accessible');
      console.log('   - CORS is not enabled');
    }
  }

  // Test 4: Check progress endpoint
  console.log('\n4️⃣  Testing GET /api/progress...');
  try {
    const response = await fetch(`${API_BASE_URL}/api/progress`);
    if (response.ok) {
      const data = await response.json();
      console.log('%c✅ Progress endpoint is working', 'color: green; font-weight: bold;');
      console.log('   Response:', data);
    } else {
      console.log('%c⚠️  Progress endpoint returned error', 'color: orange; font-weight: bold;');
      console.log('   Status:', response.status, response.statusText);
    }
  } catch (error) {
    console.log('%c❌ Progress endpoint error', 'color: red; font-weight: bold;');
    console.log('   Error:', error.message);
  }

  // Test 5: Frontend info
  console.log('\n5️⃣  Frontend Configuration:');
  console.log('   Frontend URL:', window.location.origin);
  console.log('   Backend URL:', API_BASE_URL);
  console.log('   Environment:', process.env.NODE_ENV || 'unknown');

  // Summary
  console.log('\n%c=== Diagnostic Summary ===', 'font-size: 14px; font-weight: bold; color: #6366f1;');
  console.log('\nIf you see:');
  console.log('✅ All green checks → Everything is working!');
  console.log('⚠️  Orange warnings  → Minor configuration issues (usually CORS)');
  console.log('❌ Red errors        → Backend is not running or not accessible');
  console.log('\nNext steps:');
  console.log('1. Check your backend logs');
  console.log('2. Ensure CORS is enabled (see warning messages above)');
  console.log('3. Verify backend is running on http://localhost:5000');
  console.log('4. Try refreshing this page');
}

// Run the diagnostics
runDiagnostics();

console.log('\n%cDiagnostic test complete!', 'font-size: 14px; color: #6366f1;');

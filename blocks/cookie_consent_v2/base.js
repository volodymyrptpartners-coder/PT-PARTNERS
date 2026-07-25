


// consentDict
// {
//  necessary: true,
//  preferences: false,
//  statistics: true,   // analytics_storage
//  marketing: false   // ad_storage, ad_user_data, ad_personalization
// }
function applyConsentToGtag(consentDict) {
    const consentUpdate = {
      analytics_storage: consentDict.statistics ? 'granted' : 'denied',
      ad_storage: consentDict.marketing ? 'granted' : 'denied',
      ad_user_data: consentDict.marketing ? 'granted' : 'denied',
      ad_personalization: consentDict.marketing ? 'granted' : 'denied'
    };
    
    console.log('Consent update:', consentUpdate);

    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('consent', 'update',consentUpdate);
    console.log("Update consentDict: ",consentDict);
}


function saveConsentSettings(consentDict) {
  try {
    localStorage.setItem(
      'cookie_consent_settings',
      JSON.stringify(consentDict)
    );
  } catch (e) {
    console.error('Cannot save consent:', e);
  }
}



function GetConsentChoices() {
  const keys = ['necessary', 'preferences', 'statistics', 'marketing'];

  const result = {};

  keys.forEach(function(key) {
    const el = document.getElementById('cookie_consent_v2-input_' + key);

    if (el) {
      result[key] = el.checked;
    } else {
      result[key] = false; // fallback
    }
  });
  result['necessary'] = true; // always true !!!
  return result;

}
//
// Dependecy Inversion !!!
//
// will call all functions which starts with 'ApplyConsentPolicy*'(consentDict);
function runConsentPolicies(consentDict) {
  for (const key of Object.getOwnPropertyNames(globalThis)) {
    if (typeof globalThis[key] === "function" && key.startsWith("ApplyConsentPolicy")) {
      try {
        globalThis[key](consentDict);
      } catch (e) {
        console.warn(`Error in ${key}:`, e);
      }
    }
  }
}





function ApplyConsentChoices(consentDict ) {
  applyConsentToGtag(consentDict);
  saveConsentSettings(consentDict); // because of  { necessary: true }
  restoreCheckboxes(consentDict);
  document.getElementById('cookie_consent_v2-ask_table').style.display = "none";
  document.getElementById('cookie_consent_v2-customize_table').style.display = "none";

  runConsentPolicies(consentDict);
}

function restoreCheckboxes(consentDict) {
  Object.keys(consentDict).forEach(function(key) {
    const el = document.getElementById('cookie_consent_v2-input_' + key);
    if (el) {
      el.checked = consentDict[key];
    }
  });
}

function loadConsentSettings() {
  try {
    const raw = localStorage.getItem('cookie_consent_settings');

    if (!raw) {
      // ❗ нічого нема → показуємо банер
      document.getElementById('cookie_consent_v2-ask_table').style.display = "block";
      return null;
    }

    const parsed = JSON.parse(raw);
    return parsed;

  } catch (e) {
    console.error('Cannot load consent:', e);

    // ❗ якщо JSON зламаний — теж показуємо банер
    document.getElementById('cookie_consent_v2-ask_table').style.display = "block";
    return null;
  }
}


// check if cookie is present already
document.addEventListener('DOMContentLoaded', function () {
  const consentDict =  loadConsentSettings();
  console.log("Initial ConsentDict: ", consentDict)  
  if (consentDict) {
    ApplyConsentChoices(consentDict)
  }

  document.getElementById('cookie_consent_v2-entry')
    .addEventListener('click', function() {
      document.getElementById('cookie_consent_v2-ask_table').style.display = 'block';
    });

  document.getElementById('cookie_consent_v2-customize')
    .addEventListener('click', function () {

      document.getElementById('cookie_consent_v2-customize_table').style.display = 'block';
      document.getElementById('cookie_consent_v2-ask_table').style.display = 'none';

    });

  document.getElementById('cookie_consent_v2-accept_all')
    .addEventListener('click', function () {
  
      const consent = {
        necessary: true,
        preferences: true,
        statistics: true,
        marketing: true
      };
  
      ApplyConsentChoices(consent);
    });
  
  document.getElementById('cookie_consent_v2-reject_all')
    .addEventListener('click', function () {
  
      const consent = {
        necessary: true,
        preferences: false,
        statistics: false,
        marketing: false
      };
  
      ApplyConsentChoices(consent);
    });
  
  document.getElementById('cookie_consent_v2-apply')
    .addEventListener('click', function () {
  
      const consent = GetConsentChoices();
      ApplyConsentChoices(consent);
    });
  
});

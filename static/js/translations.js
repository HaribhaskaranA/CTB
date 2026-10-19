const CTB_TRANSLATIONS = {
  en: {
    // Navigation
    nav_home: 'Home',
    nav_new_project: 'New Project',
    nav_my_projects: 'My Projects',
    nav_find_workers: 'Find Workers',
    nav_payments: 'Payments',
    nav_complaints: 'Complaints',
    nav_profile: 'Profile',
    nav_logout: 'Logout',
    nav_dashboard: 'Dashboard',
    nav_find_projects: 'Find Projects',
    nav_applications: 'Applications',
    nav_active_projects: 'Active Projects',
    nav_work_history: 'Work History',
    nav_certificates: 'Certificates',
    nav_earnings: 'Earnings',
    // Auth
    login_title: 'Login to CONNECT TO BUILD',
    login_role_owner: 'House Owner',
    login_role_worker: 'Worker / Service Provider',
    login_user_id: 'User ID',
    login_phone: 'Registered Phone Number',
    login_submit: 'Validate & Send OTP',
    otp_title: 'Verify OTP',
    otp_demo_label: 'Demo Mode — Your OTP',
    otp_verify: 'Verify OTP',
    register_owner: 'Register as House Owner',
    register_worker: 'Register as Worker',
    // Dashboard
    welcome: 'Welcome',
    new_project: 'New Project',
    my_projects: 'My Projects',
    find_workers: 'Find Workers',
    project_progress: 'Project Progress',
    payments: 'Payments',
    complaints: 'Complaints',
    notifications: 'Notifications',
    // Project
    project_type_new: 'New Construction',
    project_type_renovation: 'Renovation',
    project_type_extension: 'Extension',
    project_type_interior: 'Interior Work',
    project_type_repair: 'Repair',
    bedrooms: 'Bedrooms',
    bathrooms: 'Bathrooms',
    kitchens: 'Kitchens',
    halls: 'Halls',
    balconies: 'Balconies',
    parking: 'Parking',
    // Status
    status_pending: 'Pending',
    status_active: 'Active',
    status_completed: 'Completed',
    status_verified: 'Verified',
    status_under_review: 'Under Review',
    status_rejected: 'Rejected',
    // Common
    save: 'Save',
    cancel: 'Cancel',
    submit: 'Submit',
    confirm: 'Confirm',
    back: 'Back',
    next: 'Next',
    loading: 'Loading...',
    error_required: 'This field is required',
    demo_mode: 'Demo Mode',
    demo_disclaimer: 'This is a demonstration. No real data is used.',
  },
  ta: {
    nav_home: 'முகப்பு',
    nav_new_project: 'புதிய திட்டம்',
    nav_my_projects: 'என் திட்டங்கள்',
    nav_find_workers: 'தொழிலாளர்களை கண்டுபிடி',
    nav_payments: 'கட்டணங்கள்',
    nav_complaints: 'புகார்கள்',
    nav_profile: 'சுயவிவரம்',
    nav_logout: 'வெளியேறு',
    nav_dashboard: 'டாஷ்போர்டு',
    nav_find_projects: 'திட்டங்கள் கண்டுபிடி',
    nav_applications: 'விண்ணப்பங்கள்',
    nav_active_projects: 'செயலில் உள்ள திட்டங்கள்',
    nav_work_history: 'பணி வரலாறு',
    nav_certificates: 'சான்றிதழ்கள்',
    nav_earnings: 'வருமானம்',
    login_title: 'CONNECT TO BUILD இல் உள்நுழைக',
    login_role_owner: 'வீட்டு உரிமையாளர்',
    login_role_worker: 'தொழிலாளி / சேவை வழங்குனர்',
    login_user_id: 'பயனர் ID',
    login_phone: 'பதிவு செய்யப்பட்ட தொலைபேசி',
    login_submit: 'சரிபார்த்து OTP அனுப்பு',
    otp_title: 'OTP சரிபார்க்கவும்',
    otp_demo_label: 'டெமோ பயன்முறை — உங்கள் OTP',
    otp_verify: 'OTP சரிபார்க்கவும்',
    register_owner: 'வீட்டு உரிமையாளராக பதிவு செய்யுங்கள்',
    register_worker: 'தொழிலாளியாக பதிவு செய்யுங்கள்',
    welcome: 'வரவேற்கிறோம்',
    new_project: 'புதிய திட்டம்',
    my_projects: 'என் திட்டங்கள்',
    find_workers: 'தொழிலாளர்களை கண்டுபிடி',
    project_progress: 'திட்ட முன்னேற்றம்',
    payments: 'கட்டணங்கள்',
    complaints: 'புகார்கள்',
    notifications: 'அறிவிப்புகள்',
    bedrooms: 'படுக்கை அறைகள்',
    bathrooms: 'குளியலறைகள்',
    kitchens: 'சமையலறைகள்',
    halls: 'ஹால்கள்',
    balconies: 'பால்கனிகள்',
    parking: 'பார்க்கிங்',
    status_pending: 'நிலுவையில்',
    status_active: 'செயலில்',
    status_completed: 'முடிந்தது',
    status_verified: 'சரிபார்க்கப்பட்டது',
    status_under_review: 'ஆய்வில்',
    status_rejected: 'நிராகரிக்கப்பட்டது',
    save: 'சேமி',
    cancel: 'ரத்து',
    submit: 'சமர்ப்பி',
    confirm: 'உறுதிப்படுத்து',
    back: 'பின்',
    next: 'அடுத்து',
    loading: 'ஏற்றுகிறது...',
    error_required: 'இந்த புலம் தேவை',
    demo_mode: 'டெமோ பயன்முறை',
    demo_disclaimer: 'இது ஒரு டெமோ. உண்மையான தரவு பயன்படுத்தப்படவில்லை.',
  },
  te: {}, kn: {}, ml: {}, hi: {}
};

// Active language (from user preference, loaded from Django context)
let CTB_LANG = document.documentElement.lang || 'en';

function t(key) {
  return (CTB_TRANSLATIONS[CTB_LANG] && CTB_TRANSLATIONS[CTB_LANG][key]) ||
         CTB_TRANSLATIONS['en'][key] || key;
}

function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    el.textContent = t(key);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
  });
}

document.addEventListener('DOMContentLoaded', applyTranslations);

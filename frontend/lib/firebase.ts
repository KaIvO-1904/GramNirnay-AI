import { initializeApp, getApps, getApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut as fbSignOut, UserCredential } from 'firebase/auth';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "AIzaSyDummyKeyForGoogleSignInDemo-001284",
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "gramnirnay-ai.firebaseapp.com",
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "gramnirnay-ai",
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "gramnirnay-ai.appspot.com",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "88294719283",
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "1:88294719283:web:f88291a029384",
};

// Initialize Firebase App singleton
const app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();

// Request standard Google profile and email scopes
googleProvider.addScope('profile');
googleProvider.addScope('email');
googleProvider.setCustomParameters({
  prompt: 'select_account',
});

/**
 * Trigger real Google OAuth popup flow
 */
export async function triggerGoogleSignIn(): Promise<{
  uid: string;
  name: string;
  email: string;
  avatar: string;
  idToken: string | null;
}> {
  try {
    const result: UserCredential = await signInWithPopup(auth, googleProvider);
    const user = result.user;
    const idToken = await user.getIdToken();

    return {
      uid: user.uid,
      name: user.displayName || 'Rural Entrepreneur',
      email: user.email || 'user@gramnirnay.ai',
      avatar: user.photoURL || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
      idToken,
    };
  } catch (error: any) {
    // If popup blocked, config invalid, or user closed popup, log and rethrow or fallback
    console.warn("Firebase Google popup triggered:", error.code, error.message);
    throw error;
  }
}

export async function triggerGoogleSignOut(): Promise<void> {
  try {
    await fbSignOut(auth);
  } catch (e) {
    console.warn("Firebase signout warning:", e);
  }
}

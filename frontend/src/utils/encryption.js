import CryptoJS from 'crypto-js';

// =====================================================
// ENCRYPTION CONFIGURATION
// =====================================================
const ENCRYPTION_KEY = import.meta.env.VITE_ENCRYPTION_KEY || 'campus-archive-secret-key-2024';

// =====================================================
// ENCRYPTION FUNCTIONS
// =====================================================

/**
 * Get AES key (padded to 32 bytes)
 * @returns {string} - Key for encryption
 */
const getAESKey = () => {
  let key = ENCRYPTION_KEY;
  // Pad or truncate to 32 characters (256 bits)
  if (key.length < 32) {
    key = key.padEnd(32, '\0');
  } else if (key.length > 32) {
    key = key.substring(0, 32);
  }
  return key;
};

/**
 * Encrypt sensitive data before sending to server (compatible with backend)
 * @param {string} data - Data to encrypt
 * @returns {string} - Encrypted data as base64
 */
export const encryptData = (data) => {
  try {
    const keyString = getAESKey();
    const key = CryptoJS.enc.Utf8.parse(keyString); // Parse key as UTF-8 bytes
    const iv = CryptoJS.lib.WordArray.random(16); // 16 bytes IV

    const encrypted = CryptoJS.AES.encrypt(data, key, {
      iv: iv,
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7
    });

    // Combine IV and ciphertext, then base64 encode
    const ivCiphertext = iv.concat(encrypted.ciphertext);
    return CryptoJS.enc.Base64.stringify(ivCiphertext);
  } catch (error) {
    console.error('Encryption error:', error);
    throw new Error('Failed to encrypt data');
  }
};

/**
 * Decrypt data received from server (compatible with backend)
 * @param {string} encryptedData - Data to decrypt
 * @returns {string} - Decrypted data
 */
export const decryptData = (encryptedData) => {
  try {
    const keyString = getAESKey();
    const key = CryptoJS.enc.Utf8.parse(keyString); // Parse key as UTF-8 bytes
    const ivCiphertext = CryptoJS.enc.Base64.parse(encryptedData);

    const iv = CryptoJS.lib.WordArray.create(ivCiphertext.words.slice(0, 4)); // First 16 bytes
    const ciphertext = CryptoJS.lib.WordArray.create(ivCiphertext.words.slice(4)); // Rest

    const decrypted = CryptoJS.AES.decrypt(
      { ciphertext: ciphertext },
      key,
      {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
      }
    );

    return decrypted.toString(CryptoJS.enc.Utf8);
  } catch (error) {
    console.error('Decryption error:', error);
    throw new Error('Failed to decrypt data');
  }
};

/**
 * Encrypt sensitive fields in an object
 * @param {Object} data - Object containing data to encrypt
 * @param {Array} sensitiveFields - Array of field names to encrypt
 * @returns {Object} - Object with sensitive fields encrypted
 */
export const encryptSensitiveFields = (data, sensitiveFields = ['password', 'student_id', 'phone']) => {
  const encryptedData = { ...data };

  sensitiveFields.forEach(field => {
    if (encryptedData[field] && typeof encryptedData[field] === 'string') {
      encryptedData[field] = encryptData(encryptedData[field]);
    }
  });

  return encryptedData;
};

/**
 * Decrypt sensitive fields in an object
 * @param {Object} data - Object containing encrypted data
 * @param {Array} sensitiveFields - Array of field names to decrypt
 * @returns {Object} - Object with sensitive fields decrypted
 */
export const decryptSensitiveFields = (data, sensitiveFields = ['password', 'student_id', 'phone']) => {
  const decryptedData = { ...data };

  sensitiveFields.forEach(field => {
    if (decryptedData[field] && typeof decryptedData[field] === 'string') {
      try {
        decryptedData[field] = decryptData(decryptedData[field]);
      } catch (error) {
        // If decryption fails, keep original value (might not be encrypted)
        console.warn(`Failed to decrypt field: ${field}`);
      }
    }
  });

  return decryptedData;
};

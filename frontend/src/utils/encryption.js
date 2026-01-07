import CryptoJS from 'crypto-js';

// =====================================================
// ENCRYPTION CONFIGURATION
// =====================================================
const ENCRYPTION_KEY = import.meta.env.VITE_ENCRYPTION_KEY || 'campus-archive-secret-key-2024';

// =====================================================
// ENCRYPTION FUNCTIONS
// =====================================================

/**
 * Encrypt sensitive data before sending to server
 * @param {string} data - Data to encrypt
 * @returns {string} - Encrypted data
 */
export const encryptData = (data) => {
  try {
    return CryptoJS.AES.encrypt(data, ENCRYPTION_KEY).toString();
  } catch (error) {
    console.error('Encryption error:', error);
    throw new Error('Failed to encrypt data');
  }
};

/**
 * Decrypt data received from server
 * @param {string} encryptedData - Data to decrypt
 * @returns {string} - Decrypted data
 */
export const decryptData = (encryptedData) => {
  try {
    const bytes = CryptoJS.AES.decrypt(encryptedData, ENCRYPTION_KEY);
    return bytes.toString(CryptoJS.enc.Utf8);
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

# features/biometric.py
import platform

def biometric_available():
    system = platform.system()
    return system in ["Windows", "Darwin", "Linux"]

def biometric_unlock():
    raise NotImplementedError(
        "Biometric unlock must use OS-specific APIs such as Windows Hello, "
        "Apple Keychain/Secure Enclave, or Linux desktop keyring integration."
    )
with tab5:
    st.subheader("Biometric Unlock")
    if biometric_available():
        if st.button("Use Biometric Unlock"):
            ok, msg = biometric_unlock()
            if ok:
                st.success(msg)
                st.session_state.biometric_ok = True
            else:
                st.error(msg)
    else:
        st.info("Biometric unlock is only supported on Windows for now.")
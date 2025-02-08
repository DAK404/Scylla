# Notes

- MUST run program as `root`
- After running the keygen, source the `/etc/environment` file again in bash
- login through localhost:5000
- Use Ubuntu or Debian

---

# Important

- Did not successfully run on OpenSUSE Tumbleweed.
  - `pam` did not work.
  - Accessing `localhost:5000/login` resulted in taking me to the chat interface directly. SHOULD NOT HAPPEN!
    - [x] However, the backend did show error 401, showing that the user did not have proper credentials to access the program.
- Works just fine on Debian and Ubuntu.
  - Recommend working with Ubuntu for new users since current user's password can be used for `sudo su-`.
  - However in Debian, while setting up the system, there needs to be `root` and user password. Therefore, it is potentially difficult to navigate for new users.
  - Also using `sudo` on Debian is not as convenient as it is on Ubuntu
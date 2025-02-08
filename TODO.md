# To Do List

## Pending

### High Priority

- [ ] Add code comments
- [ ] Fix Branding image location to remote than local
- [ ] Rewrite `Readme.md`


### Low Priority

- [ ] Improve the UI, possibly looks by making Scylla chat on left and user queries on right
- [ ] Possibility to upload files to LLM
- [ ] Ability to save the chat logs and create different chats (Write the input and response to a file, with the UNIX Epoch for timestamp)

## Completed

- [x] Add prefix `Scylla> `
- [x] Test if the user can bypass login by changing URL
  - [x] Does not allow the user to access chat without login
  - [x] localhost:5000 returns with 401 bad credentials
  - [x] localhost:5000/chat returns with not configured
- [x] Ability to parse the responses from Markdown to HTML
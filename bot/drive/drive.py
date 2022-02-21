import os
import re
import pickle
import json
import logging
from tkinter import Button

from urllib.parse import urlparse, parse_qs
from random import randrange
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tenacity import *

from bot.utils import get_readable_file_size, ikb
from bot import DRIVE_ID, LOGGER, FOLDER_ID, IS_TEAM_DRIVE, USE_SERVICE_ACCOUNTS

if USE_SERVICE_ACCOUNTS:
    SERVICE_ACCOUNT_INDEX = randrange(len(os.listdir("accounts")))

class GoogleDriveHelper:
    def __init__(self, is_tg: bool = True):
        # Redirect URI for installed apps, can be left as is
        self.__G_DRIVE_DIR_MIME_TYPE = "application/vnd.google-apps.folder"
        self.__G_DRIVE_BASE_DOWNLOAD_URL = "https://drive.google.com/uc?id={}&export=download"
        self.__G_DRIVE_DIR_BASE_DOWNLOAD_URL = "https://drive.google.com/drive/folders/{}"
        self.__G_DRIVE_TOKEN_FILE = "token.pickle"
        self.__OAUTH_SCOPE = ['https://www.googleapis.com/auth/drive']
        self.__service = self.authorize()
        self.path = []

    @staticmethod
    def getIdFromUrl(link: str):
        if "folders" in link or "file" in link:
            regex = r"https://drive\.google\.com/(drive)?/?u?/?\d?/?(mobile)?/?(file)?(folders)?/?d?/([-\w]+)[?+]?/?(w+)?"
            res = re.search(regex, link)
            if res is None:
                raise IndexError("Drive ID not found")
            return res.group(5)
        parsed = urlparse(link)
        return parse_qs(parsed.query)['id'][0]

    def switchServiceAccount(self):
        global SERVICE_ACCOUNT_INDEX
        service_account_count = len(os.listdir("accounts"))
        if SERVICE_ACCOUNT_INDEX == service_account_count - 1:
            SERVICE_ACCOUNT_INDEX = 0
        SERVICE_ACCOUNT_INDEX += 1
        LOGGER.info(f"Authorizing with {SERVICE_ACCOUNT_INDEX}.json file")
        self.__service = self.authorize()

    def authorize(self):
        # Get credentials
        credentials = None
        if not USE_SERVICE_ACCOUNTS:
            if os.path.exists(self.__G_DRIVE_TOKEN_FILE):
                with open(self.__G_DRIVE_TOKEN_FILE, 'rb') as f:
                    credentials = json.loads(f)
            if credentials is None or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', self.__OAUTH_SCOPE)
                    LOGGER.info(flow)
                    credentials = flow.run_console(port=0)

                # Save the credentials for the next run
                with open(self.__G_DRIVE_TOKEN_FILE, 'wb') as token:
                    pickle.dump(credentials, token)
        else:
            LOGGER.info(f"Authorizing with {SERVICE_ACCOUNT_INDEX}.json service account")
            credentials = service_account.Credentials.from_service_account_file(
                f'accounts/{SERVICE_ACCOUNT_INDEX}.json',
                scopes=self.__OAUTH_SCOPE)
        return build('drive', 'v3', credentials=credentials, cache_discovery=False)

    def alt_authorize(self):
        credentials = None
        if USE_SERVICE_ACCOUNTS and not self.alt_auth:
            self.alt_auth = True
            if os.path.exists(self.__G_DRIVE_TOKEN_FILE):
                LOGGER.info("Authorize with token.pickle")
                with open(self.__G_DRIVE_TOKEN_FILE, 'rb') as f:
                    credentials = pickle.load(f)
                if credentials is None or not credentials.valid:
                    if credentials and credentials.expired and credentials.refresh_token:
                        credentials.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'credentials.json', self.__OAUTH_SCOPE)
                        LOGGER.info(flow)
                        credentials = flow.run_console(port=0)
                    # Save the credentials for the next run
                    with open(self.__G_DRIVE_TOKEN_FILE, 'wb') as token:
                        pickle.dump(credentials, token)
                return build('drive', 'v3', credentials=credentials, cache_discovery=False)
        return None
    
    @staticmethod
    def getIdFromUrl(link: str):
        if "folders" in link or "file" in link:
            regex = r"https://drive\.google\.com/(drive)?/?u?/?\d?/?(mobile)?/?(file)?(folders)?/?d?/([-\w]+)[?+]?/?(w+)?"
            res = re.search(regex, link)
            if res is None:
                raise IndexError("Drive ID not found")
            return res.group(5)
        parsed = urlparse(link)
        return parse_qs(parsed.query)['id'][0]

    def deleteFile(self, link: str):
        try:
            file_id = self.getIdFromUrl(link)
        except (KeyError, IndexError):
            msg = "Drive ID not found"
            LOGGER.error(f"{msg}")
            return msg
        msg = ''
        try:
            res = self.__service.files().delete(fileId=file_id, supportsTeamDrives=IS_TEAM_DRIVE).execute()
            msg = "Successfully deleted"
        except HttpError as err:
            if "File not found" in str(err):
                msg = "No such file exists"
            elif "insufficientFilePermissions" in str(err):
                msg = "Insufficient file permissions"
                token_service = self.alt_authorize()
                if token_service is not None:
                    self.__service = token_service
                    return self.deleteFile(link)
            else:
                msg = str(err)
            LOGGER.error(f"{msg}")
        finally:
            return msg

    def switchServiceAccount(self):
        global SERVICE_ACCOUNT_INDEX
        service_account_count = len(os.listdir("accounts"))
        if SERVICE_ACCOUNT_INDEX == service_account_count - 1:
            SERVICE_ACCOUNT_INDEX = 0
        SERVICE_ACCOUNT_INDEX += 1
        LOGGER.info(f"Authorizing with {SERVICE_ACCOUNT_INDEX}.json file")
        self.__service = self.authorize()

    def __set_permission(self, drive_id):
        permissions = {
            'role': 'reader',
            'type': 'anyone',
            'value': None,
            'withLink': True
        }
        return self.__service.permissions().create(supportsTeamDrives=True, fileId=drive_id,
                                                   body=permissions).execute()

    def setPerm(self, link: str):
        try:
            file_id = self.getIdFromUrl(link)
        except (KeyError, IndexError):
            msg = "Drive ID not found"
            LOGGER.error(f"{msg}")
            return msg
        msg = ''
        try:
            res = self.__set_permission(file_id)
            msg = "Successfully set permissions"
        except HttpError as err:
            if "File not found" in str(err):
                msg = "No such file exists"
            elif "insufficientFilePermissions" in str(err):
                msg = "Insufficient file permissions"
                token_service = self.alt_authorize()
                if token_service is not None:
                    self.__service = token_service
                    return self.setPerm(link)
            else:
                msg = str(err)
            LOGGER.error(f"{msg}")
        finally:
            return msg

    @retry(wait=wait_exponential(multiplier=2, min=3, max=6), stop=stop_after_attempt(5),
           retry=retry_if_exception_type(HttpError), before=before_log(LOGGER, logging.DEBUG))
    def copyFile(self, file_id, dest_id):
        body = {
            'parents': [dest_id]
        }
        try:
            return (
                self.__service.files()
                .copy(supportsAllDrives=True, fileId=file_id, body=body)
                .execute()
            )

        except HttpError as err:
            if err.resp.get('content-type', '').startswith('application/json'):
                reason = json.loads(err.content).get('error').get('errors')[0].get('reason')
                if reason in ['userRateLimitExceeded', 'dailyLimitExceeded']:
                    if USE_SERVICE_ACCOUNTS:
                        self.switchServiceAccount()
                        return self.copyFile(file_id, dest_id)
                    else:
                        LOGGER.info(f"Warning: {reason}")
                        raise err
                else:
                    raise err

    @retry(wait=wait_exponential(multiplier=2, min=3, max=6), stop=stop_after_attempt(5),
           retry=retry_if_exception_type(HttpError), before=before_log(LOGGER, logging.DEBUG))
    def getFileMetadata(self, file_id):
        return self.__service.files().get(supportsAllDrives=True, fileId=file_id,
                                              fields="name, id, mimeType, size").execute()

    @retry(wait=wait_exponential(multiplier=2, min=3, max=6), stop=stop_after_attempt(5),
           retry=retry_if_exception_type(HttpError), before=before_log(LOGGER, logging.DEBUG))
    def getFilesByFolderId(self, folder_id):
        page_token = None
        query = f"'{folder_id}' in parents and trashed = false"
        files = []
        while True:
            response = self.__service.files().list(supportsTeamDrives=True,
                                                   includeTeamDriveItems=True,
                                                   q=query,
                                                   spaces='drive',
                                                   pageSize=200,
                                                   fields='nextPageToken, files(id, name, mimeType, size)',
                                                   pageToken=page_token).execute()
            files.extend(iter(response.get('files', [])))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        return files

    def clone(self, link, parent_id: FOLDER_ID):
        self.transferred_size = 0
        self.total_files = 0
        self.total_folders = 0
        try:
            file_id = self.getIdFromUrl(link)
        except (KeyError, IndexError):
            msg = "Drive ID not found"
            LOGGER.error(f"{msg}")
            return msg
        msg = ""
        try:
            meta = self.getFileMetadata(file_id)
            if meta.get("mimeType") == self.__G_DRIVE_DIR_MIME_TYPE:
                dir_id = self.create_directory(meta.get('name'), parent_id)
                result = self.cloneFolder(meta.get('name'), meta.get('name'), meta.get('id'), dir_id)
                msg += f'<b>Filename: </b><code>{meta.get("name")}</code>'
                msg += f'\n<b>Size: </b>{get_readable_file_size(self.transferred_size)}'
                msg += '\n<b>Type: </b>Folder'
                msg += f"\n<b>SubFolders: </b>{self.total_folders}"
                msg += f"\n<b>Files: </b>{self.total_files}"
                link = self.__G_DRIVE_DIR_BASE_DOWNLOAD_URL.format(dir_id)
            else:
                file = self.copyFile(meta.get('id'), parent_id)
                try:
                    typ = file.get('mimeType')
                except:
                    typ = 'File' 
                msg += f'<b>Filename: </b><code>{file.get("name")}</code>'
                try:
                    msg += f'\n<b>Size: </b>{get_readable_file_size(int(meta.get("size", 0)))}'
                    msg += f'\n<b>Type: </b>{typ}'
                    link = self.__G_DRIVE_BASE_DOWNLOAD_URL.format(file.get("id"))
                except TypeError:
                    pass
            button = ikb({"Drive Link": link})
        except Exception as err:
            button = None
            if isinstance(err, RetryError):
                LOGGER.info(f"Total attempts: {err.last_attempt.attempt_number}")
                err = err.last_attempt.exception()
            err = str(err).replace('>', '').replace('<', '')
            LOGGER.error(err)
            if "User rate limit exceeded" in str(err):
                msg = "User rate limit exceeded"
            elif "File not found" in str(err):
                token_service = self.alt_authorize()
                if token_service is not None:
                    self.__service = token_service
                    return self.clone(link)
                msg = "No such file exists"
            else:
                msg = str(err)
            LOGGER.error(f"{msg}")
        return msg, button

    def cloneFolder(self, name, local_path, folder_id, parent_id):
        LOGGER.info(f"Syncing: {local_path}")
        files = self.getFilesByFolderId(folder_id)
        new_id = None
        if len(files) == 0:
            return parent_id
        for file in files:
            if file.get('mimeType') == self.__G_DRIVE_DIR_MIME_TYPE:
                self.total_folders += 1
                file_path = os.path.join(local_path, file.get('name'))
                current_dir_id = self.create_directory(file.get('name'), parent_id)
                new_id = self.cloneFolder(file.get('name'), file_path, file.get('id'), current_dir_id)
            else:
                try:
                    self.total_files += 1
                    self.transferred_size += int(file.get('size', 0))
                except TypeError:
                    pass
                try:
                    self.copyFile(file.get('id'), parent_id)
                    new_id = parent_id
                except Exception as e:
                    if isinstance(e, RetryError):
                        LOGGER.info(f"Total attempts: {e.last_attempt.attempt_number}")
                        err = e.last_attempt.exception()
                    else:
                        err = e
                    LOGGER.error(err)
        return new_id

    @retry(wait=wait_exponential(multiplier=2, min=3, max=6), stop=stop_after_attempt(5),
           retry=retry_if_exception_type(HttpError), before=before_log(LOGGER, logging.DEBUG))
    def create_directory(self, directory_name, parent_id):
        file_metadata = {
            "name": directory_name,
            "mimeType": self.__G_DRIVE_DIR_MIME_TYPE
        }
        if parent_id is not None:
            file_metadata["parents"] = [parent_id]
        file = self.__service.files().create(supportsTeamDrives=True, body=file_metadata).execute()
        file_id = file.get("id")
        if not IS_TEAM_DRIVE:
            self.__set_permission(file_id)
        LOGGER.info("Created: {}".format(file.get("name")))
        return file_id

    def count(self, link):
        try:
            file_id = self.getIdFromUrl(link)
        except (KeyError, IndexError):
            msg = "Drive ID not found"
            LOGGER.error(f"{msg}")
            return msg
        msg = ""
        try:
            meta = self.getFileMetadata(file_id)
            mime_type = meta.get('mimeType')
            if mime_type == self.__G_DRIVE_DIR_MIME_TYPE:
                self.gDrive_directory(meta)
                msg += f'<b>Name: </b><code>{meta.get("name")}</code>'
                msg += f'\n<b>Size: </b>{get_readable_file_size(self.total_bytes)}'
                msg += '\n<b>Type: </b>Folder'
                msg += f'\n<b>SubFolders: </b>{self.total_folders}'
                link = self.__G_DRIVE_DIR_BASE_DOWNLOAD_URL.format(file_id)
            else:
                msg += f'<b>Name: </b><code>{meta.get("name")}</code>'
                if mime_type is None:
                    mime_type = 'File'
                self.total_files += 1
                self.gDrive_file(meta)
                msg += f'\n<b>Size: </b>{get_readable_file_size(self.total_bytes)}'
                msg += f'\n<b>Type: </b>{mime_type}'
                link = self.__G_DRIVE_BASE_DOWNLOAD_URL.format(file_id)
            msg += f'\n<b>Files: </b>{self.total_files}'
            button = ikb({"Drive Link": link})
        except Exception as err:
            button = None
            if isinstance(err, RetryError):
                LOGGER.info(f"Total attempts: {err.last_attempt.attempt_number}")
                err = err.last_attempt.exception()
            err = str(err).replace('>', '').replace('<', '')
            LOGGER.error(err)
            if "File not found" in str(err):
                token_service = self.alt_authorize()
                if token_service is not None:
                    self.__service = token_service
                    return self.count(link)
                msg = "No such file exists"
            else:
                msg = str(err)
            LOGGER.error(f"{msg}")
        return msg, button

    def gDrive_file(self, filee):
        size = int(filee.get('size', 0))
        self.total_bytes += size

    def gDrive_directory(self, drive_folder):
        files = self.getFilesByFolderId(drive_folder['id'])
        if len(files) == 0:
            return
        for filee in files:
            shortcut_details = filee.get('shortcutDetails')
            if shortcut_details is not None:
                mime_type = shortcut_details['targetMimeType']
                file_id = shortcut_details['targetId']
                filee = self.getFileMetadata(file_id)
            else:
                mime_type = filee.get('mimeType')
            if mime_type == self.__G_DRIVE_DIR_MIME_TYPE:
                self.total_folders += 1
                self.gDrive_directory(filee)
            else:
                self.total_files += 1
                self.gDrive_file(filee)
    
    def drive_query(self, parent_id, fileName):
        fileName = fileName.replace("'","\\'").replace('"','\\"')
        gquery = " and ".join([f"name contains '{x}'" for x in fileName.split()])
        query = f"'{parent_id}' in parents and ({gquery})"
        return (
            self.__service.files()
            .list(
                supportsTeamDrives=True,
                includeTeamDriveItems=True,
                q=query,
                spaces='drive',
                pageSize=200,
                fields='files(id, name, mimeType, size)',
                orderBy='modifiedTime desc',
            )
            .execute()["files"]
        )

    def drive_list(self, fileName):
        data = []
        for _, parent_id in enumerate(DRIVE_ID, start=-1):
            response = self.drive_query(parent_id, fileName)
            for file in response:
                if file['mimeType'] == "application/vnd.google-apps.folder":
                    data.append(
                            {
                                "type": "folder",
                                "name": file['name'],
                                "size": "None",
                                "mimeType": "Folder",
                                "drive_url": self.__G_DRIVE_DIR_BASE_DOWNLOAD_URL.format(file['id'])
                            }
                        )
                else:
                    data.append(
                        {
                            "type": "file",
                            "name": file['name'],
                            "size": get_readable_file_size(file.get('size')),
                            "mimeType": file["mimeType"],
                            "drive_url": self.__G_DRIVE_BASE_DOWNLOAD_URL.format(file['id'])
                        }
                    )
        # if len(data) == 0:
        #     return {"error": "Found Literally Nothing"}
        return data

drive = GoogleDriveHelper()

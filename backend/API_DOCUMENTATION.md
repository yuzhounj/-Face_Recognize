# 人脸识别签到系统 API 文档

本文档描述了人脸识别签到系统后端的 API 接口。

**基础 URL**: `http://<your_server_address>:<port>` (例如: `http://127.0.0.1:5000`)

## 1. 根路径

### 1.1. 服务状态检查

*   **Endpoint**: `GET /`
*   **描述**: 检查后端服务是否正在运行。
*   **认证**: 无需
*   **请求**: 无
*   **成功响应**:
    *   **状态码**: `200 OK`
    *   **Body**:
        ```json
        {
            "message": "人脸签到系统后端正在运行! Modularized."
        }
        ```

## 2. 认证模块 (`/auth`)

### 2.1. 管理员登录

*   **Endpoint**: `POST /auth/login`
*   **描述**: 管理员使用固定凭据登录系统。成功登录后，后续需要管理员权限的请求会自动通过 session cookie 进行认证。
*   **认证**: 无需
*   **请求 Body**: `application/json`
    ```json
    {
        "username": "123",
        "password": "123"
    }
    ```
*   **参数**:
    *   `username` (string, required): 管理员用户名 (固定为 "123")。
    *   `password` (string, required): 管理员密码 (固定为 "123")。
*   **成功响应**:
    *   **状态码**: `200 OK`
    *   **Body**:
        ```json
        {
            "message": "管理员登录成功"
        }
        ```
*   **失败响应**:
    *   **状态码**: `400 Bad Request` (缺少参数)
        ```json
        {
            "message": "缺少用户名或密码"
        }
        ```
    *   **状态码**: `401 Unauthorized` (凭据错误)
        ```json
        {
            "message": "用户名或密码错误"
        }
        ```

### 2.2. 管理员登出

*   **Endpoint**: `POST /auth/logout`
*   **描述**: 管理员登出系统，清除 session。
*   **认证**: 管理员已登录
*   **请求 Body**: 无
*   **成功响应**:
    *   **状态码**: `200 OK`
    *   **Body**:
        ```json
        {
            "message": "管理员登出成功"
        }
        ```
*   **失败响应**:
    *   **状态码**: `401 Unauthorized` (管理员未登录)
        ```json
        {
            "message": "管理员未登录或权限不足"
        }
        ```

## 3. 用户管理模块 (`/user`)

### 3.1. 用户注册

*   **Endpoint**: `POST /user/register`
*   **描述**: 注册新用户，上传用户姓名和人脸照片。后端会处理照片（目前是模拟提取特征数据）并存储用户信息。
*   **认证**: 无需
*   **请求 Body**: `multipart/form-data`
    *   `name` (string, required): 用户姓名。
    *   `photo` (file, required): 用户的人脸照片文件。
*   **成功响应**:
    *   **状态码**: `201 Created`
    *   **Body**:
        ```json
        {
            "message": "用户注册成功，已存储人脸数据和照片",
            "user_id": " generated_uuid_string",
            "name": "用户提交的姓名",
            "photo_filename": "generated_unique_filename.jpg"
        }
        ```
*   **失败响应**:
    *   **状态码**: `400 Bad Request` (缺少参数或文件)
        ```json
        { "message": "缺少姓名或照片文件" }
        // 或
        { "message": "未选择照片文件" }
        ```
    *   **状态码**: `500 Internal Server Error` (人脸数据提取失败)
        ```json
        { "message": "人脸数据提取失败" }
        ```

### 3.2. 管理员注销用户

*   **Endpoint**: `DELETE /user/<user_id>`
*   **描述**: 管理员删除指定 ID 的用户。
*   **认证**: 管理员已登录
*   **URL 参数**:
    *   `user_id` (string, required): 要注销的用户的 ID。
*   **请求 Body**: 无
*   **成功响应**:
    *   **状态码**: `200 OK`
    *   **Body**:
        ```json
        {
            "message": "用户注销成功，并已删除相关照片",
            "user_id": "被注销的 user_id"
        }
        ```
*   **失败响应**:
    *   **状态码**: `401 Unauthorized` (管理员未登录)
        ```json
        { "message": "管理员未登录或权限不足" }
        ```
    *   **状态码**: `404 Not Found` (用户不存在)
        ```json
        { "message": "未找到该用户或删除失败" }
        ```

### 3.3. 管理员查看所有注册用户列表

*   **Endpoint**: `GET /user/list`
*   **描述**: 管理员获取所有已注册用户的列表，包含用户 ID, 姓名, 照片文件名以及照片的完整访问 URL。
*   **认证**: 管理员已登录
*   **请求 Body**: 无
*   **成功响应**:
    *   **状态码**: `200 OK`
    *   **Body**:
        ```json
        {
            "users": [
                {
                    "id": "uuid_string_user1",
                    "name": "姓名1",
                    "photo_filename": "filename1.jpg",
                    "photo_url": "http://<your_server_address>:<port>/uploads/filename1.jpg"
                },
                {
                    "id": "uuid_string_user2",
                    "name": "姓名2",
                    "photo_filename": "filename2.jpg",
                    "photo_url": "http://<your_server_address>:<port>/uploads/filename2.jpg"
                }
                // ... more users
            ]
        }
        // 如果没有用户，则返回:
        // { "users": [] }
        ```
*   **失败响应**:
    *   **状态码**: `401 Unauthorized` (管理员未登录)
        ```json
        { "message": "管理员未登录或权限不足" }
        ```

## 4. 签到模块 (`/attendance`)

### 4.1. 用户签到

*   **Endpoint**: `POST /attendance/sign`
*   **描述**: 用户通过上传人脸照片进行签到。后端会提取照片特征并与已注册用户的人脸数据进行比对（目前为模拟比对，总是匹配第一个注册用户）。
*   **认证**: 无需
*   **请求 Body**: `multipart/form-data`
    *   `photo` (file, required): 用于签到的人脸照片文件。
*   **成功响应**:
    *   **状态码**: `200 OK`
    *   **Body**:
        ```json
        {
            "message": "用户 [匹配到的用户名] 签到成功",
            "user_id": "匹配到的用户的 ID",
            "timestamp": "YYYY-MM-DD HH:MM:SS"
        }
        ```
*   **失败响应**:
    *   **状态码**: `400 Bad Request` (缺少文件)
        ```json
        { "message": "缺少签到照片文件" }
        // 或
        { "message": "未选择签到照片文件" }
        ```
    *   **状态码**: `404 Not Found` (未匹配到用户)
        ```json
        { "message": "签到失败：未匹配到用户" }
        ```
    *   **状态码**: `500 Internal Server Error` (人脸数据提取失败或匹配到的用户不存在等内部错误)
        ```json
        { "message": "签到照片人脸数据提取失败" }
        // 或
        { "message": "签到失败：匹配到的用户不存在" }
        ```

### 4.2. 管理员查看签到记录

*   **Endpoint**: `GET /attendance/records`
*   **描述**: 管理员查看所有用户的签到记录。
*   **认证**: 管理员已登录
*   **请求 Body**: 无
*   **成功响应**:
    *   **状态码**: `200 OK`
    *   **Body**:
        ```json
        {
            "records": [
                {
                    "user_id": "签到用户的 ID",
                    "name": "签到用户的姓名",
                    "timestamp": "YYYY-MM-DD HH:MM:SS"
                }
                // ... 更多记录
            ]
        }
        // 如果没有记录，则返回:
        // { "records": [] }
        ```
*   **失败响应**:
    *   **状态码**: `401 Unauthorized` (管理员未登录)
        ```json
        { "message": "管理员未登录或权限不足" }
        ```

## 5. 静态文件服务 (由应用直接提供)

### 5.1. 获取上传的照片

*   **Endpoint**: `GET /uploads/<filename>`
*   **描述**: 获取存储在服务器 `uploads` 文件夹中的指定照片文件。此路由通常由主应用 (`app.py`) 直接提供。
*   **认证**: 无需 (通常图片是公开访问的，如果需要保护，可以在此路由添加认证)
*   **URL 参数**:
    *   `filename` (string, required): 要获取的照片的文件名 (例如从 `/user/list` 接口中获取的 `photo_filename`)。
*   **成功响应**:
    *   **状态码**: `200 OK`
    *   **Body**: 图片的二进制数据。
    *   **Content-Type**: 图片的 MIME 类型 (例如 `image/jpeg`, `image/png`)。
*   **失败响应**:
    *   **状态码**: `404 Not Found` (文件不存在)。
    *   **状态码**: `500 Internal Server Error` (如果 `UPLOAD_FOLDER` 未配置)。

---

**注意**:
*   所有需要 `multipart/form-data` 的请求通常用于文件上传。
*   所有需要 `application/json` 的请求，其 Body 应为合法的 JSON 格式。
*   管理员权限的接口在调用前，客户端必须先成功调用 `/auth/login` 接口，并且在后续请求中携带服务端返回的 session cookie。
*   当前人脸识别逻辑为模拟，签到时会默认匹配数据库中第一个用户（如果存在）。
*   用户注册时照片会保存到服务器的 `uploads` 文件夹。前端可以通过 `/user/list` 接口获取的 `photo_url` 直接访问这些照片。

---

**注意**:
*   所有需要 `multipart/form-data` 的请求通常用于文件上传。
*   所有需要 `application/json` 的请求，其 Body 应为合法的 JSON 格式。
*   管理员权限的接口在调用前，客户端必须先成功调用 `/auth/login` 接口，并且在后续请求中携带服务端返回的 session cookie。
*   当前人脸识别逻辑为模拟，签到时会默认匹配数据库中第一个用户（如果存在）。
*   用户注册时照片会保存到服务器的 `uploads` 文件夹。前端可以通过 `/user/list` 接口获取的 `photo_url` 直接访问这些照片。 
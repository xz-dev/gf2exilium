# GF2 Exilium Spring Gachapon 自动化工具

一个用于自动完成 GF2 Exilium Spring Gachapon 活动任务的工具集，包括自动执行任务、助力、账号管理等功能。

## 快速开始

### Docker/Podman 部署

1. **构建镜像**
   ```bash
   docker build -t gf2exilium .
   ```
   或使用 Podman:
   ```bash
   podman build -t gf2exilium .
   ```

2. **运行容器**
   ```bash
   docker run -d \
     --name gf2exilium \
     -p 5000:5000 \
     -v $(pwd)/accounts.json:/app/accounts.json \
     -v $(pwd)/share_links.txt:/app/share_links.txt \
     -v $(pwd)/logs/springgachapon_play_all.log:/app/springgachapon_play_all.log \
     --restart unless-stopped \
     gf2exilium
   ```
   或使用 Podman:
   ```bash
   podman run -d \
     --name gf2exilium \
     -p 5000:5000 \
     -v $(pwd)/accounts.json:/app/accounts.json \
     -v $(pwd)/share_links.txt:/app/share_links.txt \
     -v $(pwd)/logs/springgachapon_play_all.log:/app/springgachapon_play_all.log \
     --restart unless-stopped \
     gf2exilium
   ```

3. **访问账号管理网页**
   在浏览器中打开 http://localhost:5000 访问账号管理界面

### 容器管理

- **查看容器日志**
  ```bash
  docker logs -f gf2exilium
  ```

- **查看任务执行日志**
  ```bash
  tail -f logs/springgachapon_play_all.log
  ```

- **停止容器**
  ```bash
  docker stop gf2exilium
  ```

- **重启容器**
  ```bash
  docker restart gf2exilium
  ```

- **移除容器**
  ```bash
  docker rm -f gf2exilium
  ```

## 功能简介

- **账号管理**：通过网页界面管理账号密码
- **自动执行任务**：自动完成签到、分享、抽卡等活动任务
- **自动助力**：自动为分享链接提供助力
- **定时运行**：每6小时自动运行一次任务流程
- **日志记录**：记录所有操作日志方便追踪问题

## 文件说明

- `accounts.json`: 账号信息存储文件
- `share_links.txt`: 分享链接存储文件 
- `springgachapon_play_all.log`: 任务执行日志文件

## 注意事项

- 确保运行容器前已创建必要的文件和目录
- 系统要求 Docker/Podman 环境
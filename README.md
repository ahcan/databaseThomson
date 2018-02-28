# databaseThomson
- Script syncDatabase thực hiện thêm dữ liệu Job, Node, Workflow, script được chạy liên tục sau mỗ giây
- Script syncJobparam phải chạy sau script syncDatabase và thực hiện thêm dữ liệu vào Job_param, script được chạy liên tục sau mỗi 5 phút.
run script:
  Script sync Job-Node-Workflow
   ./service_syncDatabase.sh & disown
  Script sync Job param
   ./service_syncJobparam.sh & disown
  Log file: log/syncCache.log

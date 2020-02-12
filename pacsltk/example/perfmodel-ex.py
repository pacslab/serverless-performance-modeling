from pacsltk import perfmodel

arrival_rate = 100
warm_service_time = 2
cold_service_time = 25
idle_time_before_kill = 10*60

print("arrival_rate:", arrival_rate)
print("warm_service_time:", warm_service_time)
print("cold_service_time:", cold_service_time)
print("idle_time_before_kill:", idle_time_before_kill)

props1, props2 = perfmodel.get_sls_warm_count_dist(arrival_rate, warm_service_time, cold_service_time, idle_time_before_kill)
perfmodel.print_props(props1)

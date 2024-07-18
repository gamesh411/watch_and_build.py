struct pthread_mutex_t;
struct pthread_mutexattr_t;
void pthread_mutex_init(pthread_mutex_t *mutex, const pthread_mutexattr_t *attr);
void f(pthread_mutex_t *mutex)
{
	pthread_mutex_init(mutex, 0); // no-warning
	pthread_mutex_init(mutex, 0); // expected-warning{{This lock has already been initialized}}
}

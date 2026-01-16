import { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import api from '../utils/api';
import { 
  CreditCard, FileText, Calendar, MessageSquare, 
  Bell, Settings, LogOut, TrendingUp, Users, DollarSign 
} from 'lucide-react';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [payments, setPayments] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [paymentsRes, announcementsRes, notificationsRes] = await Promise.all([
        api.get('/payments?limit=5'),
        api.get('/announcements?limit=5'),
        api.get('/notifications')
      ]);

      setPayments(paymentsRes.data.payments || []);
      setAnnouncements(announcementsRes.data.announcements || []);
      setNotifications(notificationsRes.data.notifications || []);

      if (user?.role === 'admin') {
        const statsRes = await api.get('/admin/analytics');
        setStats(statsRes.data);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background noise-texture" data-testid="dashboard">
      {/* Header */}
      <header className="bg-surface border-b border-border sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Barangay Connect</h1>
              <p className="text-sm text-muted-foreground">Welcome back, {user?.name}</p>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" className="relative" data-testid="notifications-btn">
                <Bell className="w-5 h-5" />
                {notifications.filter(n => !n.read).length > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-destructive rounded-full"></span>
                )}
              </Button>
              <Button variant="ghost" size="icon" onClick={handleLogout} data-testid="logout-btn">
                <LogOut className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Admin Stats */}
        {user?.role === 'admin' && stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <StatCard
              icon={<Users className="w-5 h-5" />}
              title="Total Members"
              value={stats.total_users}
              trend="+12%"
            />
            <StatCard
              icon={<CreditCard className="w-5 h-5" />}
              title="Total Payments"
              value={stats.total_payments}
              trend="+8%"
            />
            <StatCard
              icon={<TrendingUp className="w-5 h-5" />}
              title="Successful"
              value={stats.successful_payments}
              trend="+15%"
            />
            <StatCard
              icon={<DollarSign className="w-5 h-5" />}
              title="Total Revenue"
              value={`₱${stats.total_revenue.toLocaleString()}`}
              trend="+20%"
            />
          </div>
        )}

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <QuickAction
            icon={<CreditCard className="w-6 h-6" />}
            title="Pay Dues"
            description="Make a payment"
            to="/payments"
            testId="quick-action-payments"
          />
          <QuickAction
            icon={<FileText className="w-6 h-6" />}
            title="Documents"
            description="View library"
            to="/documents"
            testId="quick-action-documents"
          />
          <QuickAction
            icon={<Calendar className="w-6 h-6" />}
            title="Events"
            description="View calendar"
            to="/events"
            testId="quick-action-events"
          />
          <QuickAction
            icon={<MessageSquare className="w-6 h-6" />}
            title="Discussions"
            description="Join board"
            to="/discussions"
            testId="quick-action-discussions"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Payments */}
          <Card className="lg:col-span-2 rounded-2xl border-border">
            <CardHeader>
              <CardTitle>Recent Payments</CardTitle>
              <CardDescription>Your payment history</CardDescription>
            </CardHeader>
            <CardContent>
              {payments.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No payments yet</p>
              ) : (
                <div className="space-y-4">
                  {payments.map((payment) => (
                    <div key={payment.payment_id} className="flex items-center justify-between p-4 bg-muted/20 rounded-xl">
                      <div>
                        <p className="font-medium">{payment.description}</p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(payment.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-mono font-bold">₱{payment.amount.toLocaleString()}</p>
                        <StatusBadge status={payment.status} />
                      </div>
                    </div>
                  ))}
                </div>
              )}
              <Link to="/payments">
                <Button variant="ghost" className="w-full mt-4" data-testid="view-all-payments-btn">
                  View All Payments
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Announcements */}
          <Card className="rounded-2xl border-border">
            <CardHeader>
              <CardTitle>Announcements</CardTitle>
              <CardDescription>Latest from the board</CardDescription>
            </CardHeader>
            <CardContent>
              {announcements.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No announcements</p>
              ) : (
                <div className="space-y-4">
                  {announcements.map((announcement) => (
                    <div key={announcement.announcement_id} className="pb-4 border-b border-border last:border-0">
                      <h4 className="font-medium mb-1">{announcement.title}</h4>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {announcement.content}
                      </p>
                      <p className="text-xs text-muted-foreground mt-2">
                        {new Date(announcement.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              )}
              <Link to="/announcements">
                <Button variant="ghost" className="w-full mt-4" data-testid="view-all-announcements-btn">
                  View All
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, title, value, trend }) {
  return (
    <Card className="rounded-2xl border-border">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-2">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
            {icon}
          </div>
          <span className="text-xs font-medium text-green-600">{trend}</span>
        </div>
        <p className="text-2xl font-bold mb-1">{value}</p>
        <p className="text-sm text-muted-foreground">{title}</p>
      </CardContent>
    </Card>
  );
}

function QuickAction({ icon, title, description, to, testId }) {
  return (
    <Link to={to}>
      <Card className="rounded-2xl border-border hover:shadow-lg transition-all duration-300 hover:-translate-y-1 cursor-pointer" data-testid={testId}>
        <CardContent className="p-6 text-center">
          <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary mx-auto mb-3">
            {icon}
          </div>
          <h3 className="font-bold mb-1">{title}</h3>
          <p className="text-xs text-muted-foreground">{description}</p>
        </CardContent>
      </Card>
    </Link>
  );
}

function StatusBadge({ status }) {
  const colors = {
    successful: 'bg-green-100 text-green-700',
    pending: 'bg-yellow-100 text-yellow-700',
    processing: 'bg-blue-100 text-blue-700',
    failed: 'bg-red-100 text-red-700',
  };

  return (
    <span className={`text-xs px-2 py-1 rounded-full ${colors[status] || colors.pending}`}>
      {status}
    </span>
  );
}

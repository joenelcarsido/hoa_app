import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Home, Users, CreditCard, FileText, Calendar, MessageSquare, Shield } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background noise-texture">
      {/* Hero Section */}
      <div className="gradient-hero relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <img
            src="https://images.unsplash.com/photo-1727926498576-d2dd095aa117?crop=entropy&cs=srgb&fm=jpg&q=85"
            alt="Community"
            className="w-full h-full object-cover"
          />
        </div>
        
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-primary-foreground mb-6">
              Welcome to <span className="text-accent">Barangay Connect</span>
            </h1>
            <p className="text-lg sm:text-xl text-primary-foreground/90 mb-8 max-w-2xl mx-auto">
              Your complete homeowners association management platform.
              Pay dues, stay informed, and connect with your community.
            </p>
            <div className="flex gap-4 justify-center">
              <Link to="/login">
                <Button
                  size="lg"
                  data-testid="landing-login-btn"
                  className="rounded-full px-8 py-6 text-lg shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  Sign In
                </Button>
              </Link>
              <Link to="/register">
                <Button
                  size="lg"
                  variant="secondary"
                  data-testid="landing-register-btn"
                  className="rounded-full px-8 py-6 text-lg bg-white text-primary border-2 border-white/20 hover:bg-white/90"
                >
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-3xl lg:text-4xl font-bold text-center mb-12">
          Everything Your Community Needs
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <FeatureCard
            icon={<CreditCard className="w-8 h-8" />}
            title="Easy Payments"
            description="Pay your HOA dues with GCash, credit card, or PayPal. View payment history and download receipts."
          />
          <FeatureCard
            icon={<FileText className="w-8 h-8" />}
            title="Document Library"
            description="Access HOA rules, meeting minutes, and important documents anytime, anywhere."
          />
          <FeatureCard
            icon={<Calendar className="w-8 h-8" />}
            title="Event Calendar"
            description="Stay updated on community events, meetings, and important dates."
          />
          <FeatureCard
            icon={<MessageSquare className="w-8 h-8" />}
            title="Community Board"
            description="Engage with neighbors through discussion boards and announcements."
          />
          <FeatureCard
            icon={<Users className="w-8 h-8" />}
            title="Member Directory"
            description="Connect with your neighbors and board members easily."
          />
          <FeatureCard
            icon={<Shield className="w-8 h-8" />}
            title="Secure & Private"
            description="Your data is protected with industry-standard security measures."
          />
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-primary/5 py-16">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
          <p className="text-lg text-muted-foreground mb-8">
            Join your community on Barangay Connect today.
          </p>
          <Link to="/register">
            <Button size="lg" className="rounded-full px-8 py-6 text-lg" data-testid="cta-register-btn">
              Create Your Account
            </Button>
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-surface border-t border-border py-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-muted-foreground">
          <p>&copy; 2025 Barangay Connect. Built for Filipino communities.</p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, description }) {
  return (
    <div className="bg-surface rounded-2xl p-6 border border-border shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
      <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center text-primary mb-4">
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </div>
  );
}

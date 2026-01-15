import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import api from '../utils/api';
import { toast } from 'sonner';
import { CreditCard, Smartphone, DollarSign } from 'lucide-react';

export default function PaymentsPage() {
  const { user } = useAuth();
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('Monthly HOA Dues');
  const [paymentMethod, setPaymentMethod] = useState('stripe');
  const [loading, setLoading] = useState(false);

  const handlePayment = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await api.post('/payments/create', {
        amount: parseFloat(amount),
        payment_method: paymentMethod,
        description,
        metadata: {}
      });

      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      } else {
        toast.success('Payment initiated successfully');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Payment failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background noise-texture p-4 sm:p-6 lg:p-8" data-testid="payments-page">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Make a Payment</h1>
          <p className="text-muted-foreground">Pay your HOA dues securely</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Payment Form */}
          <Card className="rounded-2xl border-border">
            <CardHeader>
              <CardTitle>Payment Details</CardTitle>
              <CardDescription>Enter your payment information</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handlePayment} className="space-y-6">
                <div>
                  <Label htmlFor="amount">Amount (PHP)</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    min="100"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    required
                    data-testid="payment-amount-input"
                    className="rounded-xl h-12 font-mono text-lg"
                    placeholder="1000.00"
                  />
                  <p className="text-xs text-muted-foreground mt-1">Minimum amount: ₱100</p>
                </div>

                <div>
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    required
                    data-testid="payment-description-input"
                    className="rounded-xl h-12"
                  />
                </div>

                <div>
                  <Label className="mb-4 block">Payment Method</Label>
                  <RadioGroup value={paymentMethod} onValueChange={setPaymentMethod} className="space-y-3">
                    <div className="flex items-center space-x-3 p-4 border border-border rounded-xl hover:bg-muted/20 transition-colors">
                      <RadioGroupItem value="stripe" id="stripe" data-testid="payment-method-stripe" />
                      <Label htmlFor="stripe" className="flex items-center gap-2 cursor-pointer flex-1">
                        <CreditCard className="w-5 h-5 text-primary" />
                        <div>
                          <p className="font-medium">Credit/Debit Card</p>
                          <p className="text-xs text-muted-foreground">Powered by Stripe</p>
                        </div>
                      </Label>
                    </div>

                    <div className="flex items-center space-x-3 p-4 border border-border rounded-xl hover:bg-muted/20 transition-colors opacity-50">
                      <RadioGroupItem value="gcash" id="gcash" disabled />
                      <Label htmlFor="gcash" className="flex items-center gap-2 cursor-pointer flex-1">
                        <Smartphone className="w-5 h-5 text-primary" />
                        <div>
                          <p className="font-medium">GCash</p>
                          <p className="text-xs text-muted-foreground">Coming soon</p>
                        </div>
                      </Label>
                    </div>

                    <div className="flex items-center space-x-3 p-4 border border-border rounded-xl hover:bg-muted/20 transition-colors opacity-50">
                      <RadioGroupItem value="paypal" id="paypal" disabled />
                      <Label htmlFor="paypal" className="flex items-center gap-2 cursor-pointer flex-1">
                        <DollarSign className="w-5 h-5 text-primary" />
                        <div>
                          <p className="font-medium">PayPal</p>
                          <p className="text-xs text-muted-foreground">Coming soon</p>
                        </div>
                      </Label>
                    </div>
                  </RadioGroup>
                </div>

                <Button
                  type="submit"
                  className="w-full rounded-full h-12"
                  disabled={loading || !amount}
                  data-testid="payment-submit-btn"
                >
                  {loading ? 'Processing...' : `Pay ₱${amount || '0.00'}`}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Payment Info */}
          <div className="space-y-6">
            <Card className="rounded-2xl border-border bg-primary/5">
              <CardHeader>
                <CardTitle>Payment Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Member</span>
                  <span className="font-medium">{user?.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Unit Number</span>
                  <span className="font-medium">{user?.unit_number || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Email</span>
                  <span className="font-medium">{user?.email}</span>
                </div>
              </CardContent>
            </Card>

            <Card className="rounded-2xl border-border">
              <CardHeader>
                <CardTitle>Secure Payment</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-0.5">✓</span>
                    <span>Your payment is processed securely through Stripe</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-0.5">✓</span>
                    <span>All transactions are encrypted with 256-bit SSL</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-0.5">✓</span>
                    <span>Receive instant payment confirmation via email</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-0.5">✓</span>
                    <span>Download receipts from your payment history</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

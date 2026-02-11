import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import { useDeviceStore } from './stores/deviceStore'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import AddFriend from './pages/AddFriend'
import FriendDetail from './pages/FriendDetail'
import Pricing from './pages/Pricing'
import PaymentSuccess from './pages/PaymentSuccess'

function App() {
  const initDevice = useDeviceStore((state) => state.initDevice)

  useEffect(() => {
    initDevice()
  }, [initDevice])

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/add" element={<AddFriend />} />
          <Route path="/friend/:id" element={<FriendDetail />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/payment/success" element={<PaymentSuccess />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App

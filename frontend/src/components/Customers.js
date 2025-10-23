import React, { useState, useEffect } from 'react';
import { getCustomers, createCustomer, deleteCustomer } from '../api/api';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Plus, Trash2, Users, Phone, Mail } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Customers = () => {
  const { user } = useAuth();
  const [customers, setCustomers] = useState([]);
  const [filteredCustomers, setFilteredCustomers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isFormOpen, setIsFormOpen] = useState(false);
  
  // Estados para selección múltiple
  const [selectedCustomers, setSelectedCustomers] = useState([]);
  const [selectAll, setSelectAll] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    identification_document: '',
    address: ''
  });

  useEffect(() => {
    fetchCustomers();
  }, []);

  useEffect(() => {
    // Filtrar clientes cuando cambia el término de búsqueda
    if (searchTerm.trim() === '') {
      setFilteredCustomers(customers);
    } else {
      const filtered = customers.filter(customer =>
        customer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        customer.phone?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        customer.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        customer.identification_document?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredCustomers(filtered);
    }
  }, [searchTerm, customers]);

  const fetchCustomers = async () => {
    try {
      const response = await getCustomers();
      setCustomers(response.data);
      setFilteredCustomers(response.data);
    } catch (err) {
      setError('Error al cargar clientes');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      await createCustomer(formData);
      await fetchCustomers();
      // NO cerrar el formulario - mantenerlo abierto
      // setIsFormOpen(false);
      resetForm();
      alert('✅ Cliente agregado exitosamente. Puedes agregar otro cliente.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al guardar cliente');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('¿Estás seguro de eliminar este cliente?')) {
      try {
        await deleteCustomer(id);
        await fetchCustomers();
        alert('✅ Cliente eliminado exitosamente');
      } catch (err) {
        setError('Error al eliminar cliente');
      }
    }
  };

  // Manejar selección individual
  const handleSelectCustomer = (customerId) => {
    setSelectedCustomers(prev => {
      if (prev.includes(customerId)) {
        return prev.filter(id => id !== customerId);
      } else {
        return [...prev, customerId];
      }
    });
  };

  // Manejar seleccionar todos
  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedCustomers([]);
      setSelectAll(false);
    } else {
      setSelectedCustomers(filteredCustomers.map(c => c.id));
      setSelectAll(true);
    }
  };

  // Eliminar seleccionados
  const handleDeleteSelected = async () => {
    if (selectedCustomers.length === 0) {
      alert('No hay clientes seleccionados');
      return;
    }
    
    if (window.confirm(`¿Estás seguro de eliminar ${selectedCustomers.length} cliente(s)?`)) {
      try {
        // Eliminar todos los seleccionados
        await Promise.all(selectedCustomers.map(id => deleteCustomer(id)));
        setSelectedCustomers([]);
        setSelectAll(false);
        await fetchCustomers();
      } catch (err) {
        setError('Error al eliminar clientes');
        console.error(err);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      phone: '',
      email: '',
      identification_document: '',
      address: ''
    });
  };

  if (loading) {
    return <div className="text-center py-8">Cargando...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Clientes</h2>
          <p className="text-gray-500 mt-1">Gestiona tu base de clientes</p>
        </div>
        <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => resetForm()}>
              <Plus className="mr-2 h-4 w-4" /> Nuevo Cliente
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Nuevo Cliente</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label>Nombre Completo *</Label>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Nombre del cliente"
                  required
                />
              </div>

              <div>
                <Label>Teléfono *</Label>
                <Input
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="809-123-4567"
                  required
                />
              </div>

              <div>
                <Label>Cedula/Pasaporte/RNC (Opcional)</Label>
                <Input
                  value={formData.identification_document}
                  onChange={(e) => setFormData({ ...formData, identification_document: e.target.value })}
                  placeholder="001-1234567-8"
                />
              </div>

              <div>
                <Label>Email (Opcional)</Label>
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="cliente@ejemplo.com"
                />
              </div>

              <div>
                <Label>Dirección (Opcional)</Label>
                <textarea
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  className="w-full p-2 border rounded-md"
                  rows="2"
                  placeholder="Dirección del cliente"
                />
              </div>

              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => setIsFormOpen(false)}>
                  Cancelar
                </Button>
                <Button type="submit">
                  Guardar Cliente
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {error && !isFormOpen && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center flex-wrap gap-4">
            <CardTitle>Lista de Clientes ({filteredCustomers.length})</CardTitle>
            <div className="flex items-center space-x-2">
              {selectedCustomers.length > 0 && user?.role === 'admin' && (
                <Button
                  onClick={handleDeleteSelected}
                  variant="destructive"
                  size="sm"
                  className="flex items-center"
                >
                  <Trash2 size={16} className="mr-2" />
                  Eliminar Seleccionados ({selectedCustomers.length})
                </Button>
              )}
              <div className="w-64">
                <input
                  type="text"
                  placeholder="Buscar por nombre, teléfono, email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                />
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  {user?.role === 'admin' && (
                    <th className="text-left p-2 text-sm font-medium w-12">
                      <input
                        type="checkbox"
                        checked={selectAll}
                        onChange={handleSelectAll}
                        className="w-4 h-4 cursor-pointer"
                        title="Seleccionar todos"
                      />
                    </th>
                  )}
                  <th className="text-left p-2 text-sm font-medium">Nombre</th>
                  <th className="text-left p-2 text-sm font-medium">Teléfono</th>
                  <th className="text-left p-2 text-sm font-medium">Cedula/Pasaporte/RNC</th>
                  <th className="text-left p-2 text-sm font-medium">Email</th>
                  <th className="text-center p-2 text-sm font-medium">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filteredCustomers.length > 0 ? (
                  filteredCustomers.map((customer) => (
                    <tr key={customer.id} className="border-b hover:bg-gray-50">
                      {user?.role === 'admin' && (
                        <td className="p-2 text-sm">
                          <input
                            type="checkbox"
                            checked={selectedCustomers.includes(customer.id)}
                            onChange={() => handleSelectCustomer(customer.id)}
                            className="w-4 h-4 cursor-pointer"
                          />
                        </td>
                      )}
                      <td className="p-2 text-sm">{customer.name}</td>
                      <td className="p-2 text-sm">
                        <div className="flex items-center">
                          <Phone size={14} className="mr-1 text-gray-500" />
                          {customer.phone}
                        </div>
                      </td>
                      <td className="p-2 text-sm">
                        {customer.identification_document || customer.dni || '-'}
                      </td>
                      <td className="p-2 text-sm">
                        {customer.email && (
                          <div className="flex items-center">
                            <Mail size={14} className="mr-1 text-gray-500" />
                            {customer.email}
                          </div>
                        )}
                      </td>
                      <td className="p-2 text-sm">
                        <div className="flex justify-center space-x-2">
                          {user?.role === 'admin' && (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleDelete(customer.id)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <Trash2 size={16} />
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="5" className="text-center py-8 text-gray-500">
                      No hay clientes registrados
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Customers;

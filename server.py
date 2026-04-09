import os

ARCHIVO_PRODUCTOS = "productos.json"

def cargar_productos():
    if os.path.exists(ARCHIVO_PRODUCTOS):
        with open(ARCHIVO_PRODUCTOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def guardar_productos(data):
    with open(ARCHIVO_PRODUCTOS, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)



from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# Datos iniciales
productos = [
    {"id": 1, "nombre": "Lapiz Para Carpintero BI-COLOR", "precio": 8.19, "stock": 1},
    {"id": 2, "nombre": "Cinta Masking TAPE GENERAL", "precio": 94.80, "stock": 1}
]

usuarios = [
    {"usuario": "admin", "clave": "admin123", "rol": "admin"},
    {"usuario": "vendedor", "clave": "1234", "rol": "vendedor"}
]

mensajes = []

class MiServidor(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="UTF-8">
              <title>Catálogo Profesional</title>
              <style>
                body { font-family: Arial; margin: 20px; background: #f4f4f9; }
                h1, h2 { color: #333; }
                table { border-collapse: collapse; width: 70%; margin-bottom: 20px; }
                th, td { border: 1px solid #ccc; padding: 10px; text-align: left; }
                th { background: #eee; }
                input, button { padding: 5px 10px; margin: 5px 0; }
                #mensajes { border: 1px solid #ccc; padding: 10px; width: 50%; max-height: 200px; overflow-y: auto; background: #fff; }
              </style>
            </head>
            <body>
              <h1>Catálogo de Productos</h1>
              <table>
                <thead>
                  <tr><th>ID</th><th>Nombre</th><th>Precio</th><th>Stock</th></tr>
                </thead>
                <tbody id="lista"></tbody>
              </table>

              <div id="adminMenu" style="display:none;">
                <h2>Administración (solo admin)</h2>
                <table>
                  <thead>
                    <tr><th>ID</th><th>Nombre</th><th>Precio</th><th>Stock</th><th>Acción</th></tr>
                  </thead>
                  <tbody id="listaAdmin"></tbody>
                </table>

                <h3>Agregar Producto</h3>
                <form id="formAgregar">
                  <input type="text" id="id" placeholder="ID" required>
                  <input type="text" id="nombre" placeholder="Nombre" required>
                  <input type="number" id="precio" placeholder="Precio" required>
                  <input type="number" id="stock" placeholder="Stock" required>
                  <button type="submit">Agregar</button>
                </form>
              </div>

              <h2>Mensajes Internos</h2>
              <div id="mensajes"></div>
              <input type="text" id="nuevoMensaje" placeholder="Escribe un mensaje">
              <button onclick="enviarMensaje()">Enviar</button>

              <h2>Login</h2>
              <input type="text" id="usuario" placeholder="Usuario">
              <input type="password" id="clave" placeholder="Contraseña">
              <input type="text" id="nickname" placeholder="Nickname">
              <button onclick="login()">Login</button>

              <script>
                function cargarProductos() {
                  fetch('/productos')
                    .then(res => res.json())
                    .then(data => {
                      const tbody = document.getElementById('lista');
                      tbody.innerHTML = '';
                      data.forEach(p => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `<td>${p.id}</td><td>${p.nombre}</td><td>${p.precio}</td><td>${p.stock}</td>`;
                        tbody.appendChild(tr);
                      });
                      cargarProductosAdmin();
                    });
                }

                function cargarProductosAdmin() {
                  const rol = sessionStorage.getItem('rol');
                  if(rol !== 'admin') return;
                  fetch('/productos')
                    .then(res => res.json())
                    .then(data => {
                      const tbody = document.getElementById('listaAdmin');
                      tbody.innerHTML = '';
                      data.forEach(p => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `<td>${p.id}</td><td>${p.nombre}</td><td>${p.precio}</td><td>${p.stock}</td>
                                        <td>
                                          <button onclick="actualizarStock(${p.id}, 1)">+</button>
                                          <button onclick="actualizarStock(${p.id}, -1)">-</button>
                                        </td>`;
                        tbody.appendChild(tr);
                      });
                    });
                }

                function actualizarStock(id, cambio) {
                  fetch('/stock/' + id, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({stock: cambio})
                  }).then(() => cargarProductos());
                }

                document.getElementById('formAgregar').onsubmit = function(e) {
                  e.preventDefault();
                  const nuevo = {
                    id: parseInt(document.getElementById('id').value),
                    nombre: document.getElementById('nombre').value,
                    precio: parseFloat(document.getElementById('precio').value),
                    stock: parseInt(document.getElementById('stock').value)
                  };
                  fetch('/agregar', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(nuevo)
                  }).then(() => {
                    cargarProductos();
                    document.getElementById('formAgregar').reset();
                  });
                }

                function cargarMensajes() {
                  fetch('/mensajes')
                    .then(res => res.json())
                    .then(data => {
                      const div = document.getElementById('mensajes');
                      div.innerHTML = '';
                      data.forEach(m => { div.innerHTML += `<p>${m.nickname}: ${m.texto}</p>`; });
                    });
                }

                function enviarMensaje() {
                  const texto = document.getElementById('nuevoMensaje').value;
                  const nickname = sessionStorage.getItem('nickname') || 'Invitado';
                  if(texto.trim() === '') return;
                  fetch('/mensajes', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({nickname, texto})
                  }).then(() => {
                    document.getElementById('nuevoMensaje').value = '';
                    cargarMensajes();
                  });
                }

                function login() {
                  const usuario = document.getElementById('usuario').value;
                  const clave = document.getElementById('clave').value;
                  const nickname = document.getElementById('nickname').value || usuario;
                  fetch('/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({usuario, clave})
                  }).then(res => res.json())
                    .then(r => {
                      alert(r.mensaje);
                      if(r.rol) {
                        sessionStorage.setItem('rol', r.rol);
                        sessionStorage.setItem('nickname', nickname);
                        mostrarMenu();
                      }
                    });
                }

                function mostrarMenu() {
                  const rol = sessionStorage.getItem('rol');
                  if(rol === 'admin') {
                    document.getElementById('adminMenu').style.display = 'block';
                    cargarProductosAdmin();
                  }
                }

                cargarProductos();
                cargarMensajes();
              </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))

        elif self.path == "/productos":
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(productos).encode('utf-8'))

        elif self.path == "/mensajes":
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(mensajes).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        if self.path == "/agregar":
            productos.append(data)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Producto agregado")
        elif self.path == "/mensajes":
            mensajes.append({"nickname": data['nickname'], "texto": data['texto']})
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Mensaje recibido")
        elif self.path == "/login":
            encontrado = None
            for u in usuarios:
                if u['usuario'] == data['usuario'] and u['clave'] == data['clave']:
                    encontrado = u
                    break
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            if encontrado:
                self.wfile.write(json.dumps({"mensaje":"Login exitoso","rol":encontrado['rol']}).encode('utf-8'))
            else:
                self.wfile.write(json.dumps({"mensaje":"Usuario o clave incorrectos"}).encode('utf-8'))

    def do_PUT(self):
        if self.path.startswith("/stock/"):
            id_producto = int(self.path.split("/")[-1])
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            for p in productos:
                if p['id'] == id_producto:
                    p['stock'] += data.get('stock',0)
                    if p['stock'] < 0:
                        p['stock'] = 0
                    break
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Stock actualizado")

PORT = 3000
server = HTTPServer(('localhost', PORT), MiServidor)
print(f"Servidor corriendo en http://localhost:{PORT}")
server.serve_forever()
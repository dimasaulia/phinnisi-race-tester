import customtkinter as ctk
import requests
import threading
import time
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox, scrolledtext, filedialog


class AutoHitApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Phinnisi Race Tester")
        self.root.geometry("800x700")

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_frame, text="Phinnisi Race Tester", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=(0, 20))

        # URL and Method section
        url_frame = ctk.CTkFrame(main_frame)
        url_frame.pack(fill="x", padx=10, pady=(0, 15))

        ctk.CTkLabel(url_frame, text="URL:", font=ctk.CTkFont(
            weight="bold")).pack(anchor="w", padx=15, pady=(15, 5))
        self.url_entry = ctk.CTkEntry(
            url_frame, placeholder_text="https://api.example.com/endpoint")
        self.url_entry.pack(fill="x", padx=15, pady=(0, 10))

        method_frame = ctk.CTkFrame(url_frame)
        method_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(method_frame, text="Method:", font=ctk.CTkFont(
            weight="bold")).pack(anchor="w", pady=(0, 5))
        self.method_var = ctk.StringVar(value="GET")
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]

        method_buttons_frame = ctk.CTkFrame(method_frame)
        method_buttons_frame.pack(fill="x", pady=(0, 10))

        for i, method in enumerate(methods):
            btn = ctk.CTkRadioButton(
                method_buttons_frame, text=method, variable=self.method_var, value=method)
            btn.grid(row=0, column=i, padx=10, pady=5, sticky="w")

        # Headers and Body tabs
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        # Headers tab
        headers_tab = self.tabview.add("Headers")
        ctk.CTkLabel(headers_tab, text="Headers (JSON format):", font=ctk.CTkFont(
            weight="bold")).pack(anchor="w", pady=(10, 5))
        self.headers_text = ctk.CTkTextbox(headers_tab, height=150)
        self.headers_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.headers_text.insert(
            "0.0", '{\n  "Content-Type": "application/json",\n  "Authorization": "Bearer your-token"\n}')

        # Body tab
        body_tab = self.tabview.add("Body")
        ctk.CTkLabel(body_tab, text="JSON Body:", font=ctk.CTkFont(
            weight="bold")).pack(anchor="w", pady=(10, 5))
        self.body_text = ctk.CTkTextbox(body_tab, height=150)
        self.body_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.body_text.insert("0.0", '{\n  "key": "value"\n}')

        # Configuration section
        config_frame = ctk.CTkFrame(main_frame)
        config_frame.pack(fill="x", padx=10, pady=(0, 15))

        ctk.CTkLabel(config_frame, text="Test Configuration", font=ctk.CTkFont(
            size=16, weight="bold")).pack(pady=(15, 10))

        # Virtual users
        users_frame = ctk.CTkFrame(config_frame)
        users_frame.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(users_frame, text="Virtual Users:").pack(
            side="left", padx=(10, 5))
        self.virtual_users_var = ctk.StringVar(value="2")
        self.virtual_users_entry = ctk.CTkEntry(
            users_frame, textvariable=self.virtual_users_var, width=80)
        self.virtual_users_entry.pack(side="left", padx=(0, 10))

        # Requests per user
        ctk.CTkLabel(users_frame, text="Requests per User:").pack(
            side="left", padx=(20, 5))
        self.requests_var = ctk.StringVar(value="5")
        self.requests_entry = ctk.CTkEntry(
            users_frame, textvariable=self.requests_var, width=80)
        self.requests_entry.pack(side="left", padx=(0, 10))

        # Delay between requests
        delay_frame = ctk.CTkFrame(config_frame)
        delay_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(delay_frame, text="Delay between requests (seconds):").pack(
            side="left", padx=(10, 5))
        self.delay_var = ctk.StringVar(value="0.1")
        self.delay_entry = ctk.CTkEntry(
            delay_frame, textvariable=self.delay_var, width=80)
        self.delay_entry.pack(side="left", padx=(0, 10))

        # Control buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=(0, 15))

        self.start_button = ctk.CTkButton(button_frame, text="Start Test", command=self.start_test,
                                          font=ctk.CTkFont(size=16, weight="bold"), height=40)
        self.start_button.pack(side="left", padx=(15, 10), pady=15)

        self.stop_button = ctk.CTkButton(button_frame, text="Stop Test", command=self.stop_test,
                                         font=ctk.CTkFont(size=16, weight="bold"), height=40,
                                         fg_color="red", hover_color="darkred")
        self.stop_button.pack(side="left", padx=(0, 10), pady=15)
        self.stop_button.configure(state="disabled")
        
        self.save_button = ctk.CTkButton(button_frame, text="Save Results", command=self.save_results,
                                        font=ctk.CTkFont(size=16, weight="bold"), height=40,
                                        fg_color="green", hover_color="darkgreen")
        self.save_button.pack(side="left", padx=(0, 15), pady=15)
        self.save_button.configure(state="disabled")

        # Results section
        results_frame = ctk.CTkFrame(main_frame)
        results_frame.pack(fill="both", expand=True, padx=10)

        results_header_frame = ctk.CTkFrame(results_frame)
        results_header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(results_header_frame, text="Results", font=ctk.CTkFont(
            size=16, weight="bold")).pack(side="left")
            
        self.summary_label = ctk.CTkLabel(results_header_frame, text="", font=ctk.CTkFont(size=12))
        self.summary_label.pack(side="right")

        self.results_text = ctk.CTkTextbox(results_frame, height=200)
        self.results_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.is_running = False
        self.executor = None
        self.log_data = []
        self.test_summary = {}

    def start_test(self):
        try:
            # Validate inputs
            url = self.url_entry.get().strip()
            if not url:
                messagebox.showerror("Error", "URL is required!")
                return

            virtual_users = int(self.virtual_users_var.get())
            requests_per_user = int(self.requests_var.get())
            delay = float(self.delay_var.get())

            if virtual_users <= 0 or requests_per_user <= 0:
                messagebox.showerror(
                    "Error", "Virtual users and requests must be greater than 0!")
                return

            # Parse headers
            headers = {}
            headers_text = self.headers_text.get("0.0", "end-1c").strip()
            if headers_text:
                try:
                    headers = json.loads(headers_text)
                except json.JSONDecodeError:
                    messagebox.showerror(
                        "Error", "Invalid JSON format in Headers!")
                    return

            # Parse body
            body_data = None
            body_text = self.body_text.get("0.0", "end-1c").strip()
            if body_text and self.method_var.get() in ["POST", "PUT", "PATCH"]:
                try:
                    body_data = json.loads(body_text)
                except json.JSONDecodeError:
                    messagebox.showerror(
                        "Error", "Invalid JSON format in Body!")
                    return

            # Start testing
            self.is_running = True
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.save_button.configure(state="disabled")
            self.results_text.delete("0.0", "end")
            self.log_data = []
            self.test_summary = {
                "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "url": url,
                "method": self.method_var.get(),
                "virtual_users": virtual_users,
                "requests_per_user": requests_per_user,
                "delay": delay,
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0
            }
            
            start_log = f"Starting test with {virtual_users} virtual users, {requests_per_user} requests each...\n\n"
            self.results_text.insert("0.0", start_log)
            self.log_data.append(start_log)

            # Start test in background thread
            test_thread = threading.Thread(target=self.run_test,
                                           args=(url, self.method_var.get(), headers, body_data,
                                                 virtual_users, requests_per_user, delay))
            test_thread.daemon = True
            test_thread.start()

        except ValueError:
            messagebox.showerror(
                "Error", "Please enter valid numbers for configuration!")

    def stop_test(self):
        self.is_running = False
        if self.executor:
            self.executor.shutdown(wait=False)
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        if self.log_data:
            self.save_button.configure(state="normal")
        self.log_result("Test stopped by user.\n")

    def run_test(self, url, method, headers, body_data, virtual_users, requests_per_user, delay):
        self.executor = ThreadPoolExecutor(max_workers=virtual_users)
        futures = []

        start_time = time.time()

        for user_id in range(virtual_users):
            if not self.is_running:
                break

            future = self.executor.submit(self.simulate_user, user_id + 1, url, method,
                                          headers, body_data, requests_per_user, delay)
            futures.append(future)

        # Wait for all users to complete
        for future in futures:
            if not self.is_running:
                break
            future.result()

        end_time = time.time()
        total_time = end_time - start_time

        if self.is_running:
            completion_log = f"\nTest completed in {total_time:.2f} seconds\n"
            total_log = f"Total requests sent: {virtual_users * requests_per_user}\n"
            success_log = f"Successful: {self.test_summary['successful_requests']} | Failed: {self.test_summary['failed_requests']}\n"
            
            self.log_result(completion_log)
            self.log_result(total_log)
            self.log_result(success_log)
            
            self.test_summary["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.test_summary["duration"] = total_time
            
            # Update summary display
            summary_text = f"Success: {self.test_summary['successful_requests']}/{self.test_summary['total_requests']} | Duration: {total_time:.2f}s"
            self.summary_label.configure(text=summary_text)

        self.root.after(0, self.test_completed)

    def simulate_user(self, user_id, url, method, headers, body_data, requests_count, delay):
        for request_num in range(requests_count):
            if not self.is_running:
                break

            try:
                start_time = time.time()
                timestamp = time.strftime(
                    "%H:%M:%S", time.localtime(start_time))

                if method == "GET":
                    response = requests.get(url, headers=headers, timeout=30)
                elif method == "POST":
                    response = requests.post(
                        url, headers=headers, json=body_data, timeout=30)
                elif method == "PUT":
                    response = requests.put(
                        url, headers=headers, json=body_data, timeout=30)
                elif method == "DELETE":
                    response = requests.delete(
                        url, headers=headers, timeout=30)
                elif method == "PATCH":
                    response = requests.patch(
                        url, headers=headers, json=body_data, timeout=30)

                response_time = time.time() - start_time

                # Log detailed information
                log_entry = {
                    "timestamp": timestamp,
                    "user_id": user_id,
                    "request_num": request_num + 1,
                    "method": method,
                    "url": url,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "response_headers": dict(response.headers),
                    "success": response.status_code < 400
                }
                
                # Try to parse response body
                try:
                    log_entry["response_body"] = response.json()
                    response_display = json.dumps(log_entry["response_body"], indent=2)
                except json.JSONDecodeError:
                    log_entry["response_body"] = response.text
                    response_display = response.text[:500]
                    if len(response.text) > 500:
                        response_display += "..."
                
                self.log_data.append(log_entry)
                
                # Update counters
                self.test_summary["total_requests"] += 1
                if response.status_code < 400:
                    self.test_summary["successful_requests"] += 1
                else:
                    self.test_summary["failed_requests"] += 1
                
                # Display in UI
                self.log_result(
                    f"[{timestamp}] User {user_id} - Request {request_num + 1}\n")
                self.log_result(f"  Method: {method} | URL: {url}\n")
                self.log_result(
                    f"  Status: {response.status_code} | Response Time: {response_time:.3f}s\n")
                self.log_result(
                    f"  Response Headers: {dict(response.headers)}\n")
                self.log_result(
                    f"  Response Body: {response_display}\n")
                self.log_result("-" * 80 + "\n\n")

            except requests.exceptions.RequestException as e:
                timestamp = time.strftime("%H:%M:%S", time.localtime())
                
                # Log error entry
                error_entry = {
                    "timestamp": timestamp,
                    "user_id": user_id,
                    "request_num": request_num + 1,
                    "method": method,
                    "url": url,
                    "error": str(e),
                    "success": False
                }
                
                self.log_data.append(error_entry)
                self.test_summary["total_requests"] += 1
                self.test_summary["failed_requests"] += 1
                
                self.log_result(
                    f"[{timestamp}] User {user_id} - Request {request_num + 1}\n")
                self.log_result(f"  Method: {method} | URL: {url}\n")
                self.log_result(f"  ERROR: {str(e)}\n")
                self.log_result("-" * 80 + "\n\n")

            if delay > 0 and request_num < requests_count - 1:
                time.sleep(delay)

    def log_result(self, message):
        self.root.after(0, lambda: self.results_text.insert("end", message))
        self.root.after(0, lambda: self.results_text.see("end"))

    def save_results(self):
        if not self.log_data:
            messagebox.showwarning("Warning", "No test results to save!")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"api_test_results_{timestamp}.json"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialname=default_filename
        )
        
        if file_path:
            try:
                results_data = {
                    "test_summary": self.test_summary,
                    "requests": self.log_data
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(results_data, f, indent=2, ensure_ascii=False)
                    
                messagebox.showinfo("Success", f"Results saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def test_completed(self):
        self.is_running = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.save_button.configure(state="normal")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = AutoHitApp()
    app.run()

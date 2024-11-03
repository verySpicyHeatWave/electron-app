import ctypes
import json
import logging
import queue
import threading
import pika
import random
import sys
import time
import tkinter as tk

WIN_W: int = 600
WIN_H: int = 400

class MainWindow(tk.Tk):
    def __init__(self, exchange = "data1"):
        # Main Window Configuration
        super().__init__(None)
        self.title('Fake Battery Data Generator')
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.config(background = "white")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(True, True)
        self.verify_entry_is_number = (self.register(self.numentry_verify_callback))
        self.exchange = exchange

        # Instance fields
        self.producer_thread: DataProducer = DataProducer(parent=self, exchange=self.exchange)
        self.cellvars = [tk.DoubleVar(None, value=3.5),
                         tk.DoubleVar(None, value=3.5),
                         tk.DoubleVar(None, value=3.5),
                         tk.DoubleVar(None, value=3.5),
                         tk.DoubleVar(None, value=3.5),
                         tk.DoubleVar(None, value=3.5),
                         tk.DoubleVar(None, value=3.5),
                         tk.DoubleVar(None, value=3.5)]
        self.pnvar = tk.IntVar(None, 102051000)
        self.snvar = tk.IntVar(None, 1)
        self.currentvar = tk.DoubleVar(None, value=0)
        self.dpovar = tk.BooleanVar(None, value=False)
        self.tempvars = {
            "pack" : tk.IntVar(None, 25),
            "bms" : tk.IntVar(None, 25),
            "dfet" : tk.IntVar(None, 25),
            "cfet" : tk.IntVar(None, 25),
            "board" : tk.IntVar(None, 25)
        }

        # Define widgets
        self.startstop: tk.Button = tk.Button(self, text="Start/Stop Dataflow", command=self.toggle_stream, anchor='n')
        self.status: tk.Label = tk.Label(self, text="Stopped", font=("Segoe-UI", 18, "bold"), fg="black", bg="white", anchor='n')
        cellv_frame: tk.Frame = self.create_cellv_frame()
        pnsn_frame: tk.Frame = self.create_pnsn_frame()
        other_frame: tk.Frame = self.create_other_frame()
        temp_frame: tk.Frame = self.create_temp_frame()

        # Place widgets
        self.startstop.grid(row=0, column=0, padx=20, pady=(20,0))
        self.status.grid(row=0, column=1, padx=20, pady=(20,0), sticky='nsew')
        cellv_frame.grid(row=1, column=0, padx=20, pady=20, rowspan=2, sticky='nsew')
        pnsn_frame.grid(row=1, column=1, padx=20, pady=20, sticky='nsew')
        other_frame.grid(row=2, column=1, padx=20, pady=20, sticky='nsew')
        temp_frame.grid(row=1, column=2, padx=20, pady=20, rowspan=2, sticky='nsew')


    def create_cellv_frame(self):
        cellv_frame: tk.Frame = tk.Frame(self)
        for i in range(1,9):
            lbl: tk.Label = tk.Label(cellv_frame, text=f"cell {i}:")
            num: tk.Spinbox = tk.Spinbox(cellv_frame, from_=2.7, to=4.3, increment=0.1,
                                         textvariable=self.cellvars[i-1], width=7)
            lbl.grid(row=i-1, column=0, padx=10, pady=10)
            num.grid(row=i-1, column=1, padx=10, pady=10)        
        return cellv_frame

    def create_pnsn_frame(self):
        pnsn_frame: tk.Frame = tk.Frame(self)
        lbl1: tk.Label = tk.Label(pnsn_frame, text=f"battery pn: ")
        pnent: tk.Entry = tk.Entry(pnsn_frame, textvariable=self.pnvar, width=12,
                                   validate='all', validatecommand=(self.verify_entry_is_number, '%P'))
        lbl2: tk.Label = tk.Label(pnsn_frame, text=f"battery sn: ")
        snent: tk.Entry = tk.Entry(pnsn_frame, textvariable=self.snvar, width=12,
                                   validate='all', validatecommand=(self.verify_entry_is_number, '%P'))
        lbl1.grid(row=0, column=0, padx=10, pady=10)
        pnent.grid(row=0, column=1, padx=10, pady=10)
        lbl2.grid(row=1, column=0, padx=10, pady=10)
        snent.grid(row=1, column=1, padx=10, pady=10)
        return pnsn_frame
    
    def create_other_frame(self):
        other_frame: tk.Frame = tk.Frame(self)
        lbl: tk.Label = tk.Label(other_frame, text=f"current:")
        box: tk.Spinbox = tk.Spinbox(other_frame, from_=0, to=144, increment=1,
                                        textvariable=self.currentvar, width=7)
        ckbx: tk.Checkbutton = tk.Checkbutton(other_frame, text="dpo en?", variable=self.dpovar)
        lbl.grid(row=0, column=0, padx=10, pady=10)
        box.grid(row=0, column=1, padx=10, pady=10)
        ckbx.grid(row=1, column=0, padx=20, pady=20, columnspan=2)
        return other_frame
    
    def create_temp_frame(self):
        temp_frame: tk.Frame = tk.Frame(self)
        for i, key in enumerate(self.tempvars.keys()):
            lbl: tk.Label = tk.Label(temp_frame, text=f"{key} temp:")
            num: tk.Spinbox = tk.Spinbox(temp_frame, from_=-40, to=40, increment=1,
                                         textvariable=self.tempvars[key], width=7)
            lbl.grid(row=i, column=0, padx=10, pady=10)
            num.grid(row=i, column=1, padx=10, pady=10)
        return temp_frame

    def toggle_stream(self):
        if self.producer_thread.is_alive():
            self.producer_thread.kill_stream()
            self.producer_thread.join()
            print("Ending stream...\n\n")
            self.status.config(text="Stopped", fg="black")
        else:
            self.producer_thread = DataProducer(parent=self, exchange=self.exchange)
            self.producer_thread.start()
            self.status.config(text="Running", fg="red")

    def on_closing(self):
        if self.producer_thread.is_alive():
            self.producer_thread.kill_stream()
            self.producer_thread.join()
            print("Ending stream...\n\n")
        self.close_exchange()
        self.destroy()
    
    def numentry_verify_callback(self, P):
        return str.isdigit(P) or str(P) == ""
    

    def close_exchange(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
        channel = connection.channel()
        channel.exchange_delete(self.exchange)





class DataProducer(threading.Thread):
    def __init__(self, parent: MainWindow, exchange: str):
        super().__init__(None)
        self.parent = parent
        self.exchange = exchange
        self.logging = False        
        self.subscriber = queue.Queue(maxsize=5)
        self.vals = {
            "battery_pn" : 0,
            "battery_sn" : 0,
            "pack_voltage" : 0,
            "pack_current" : 0,
            "cell1_voltage" : 0,
            "cell2_voltage" : 0,
            "cell3_voltage" : 0,
            "cell4_voltage" : 0,
            "cell5_voltage" : 0,
            "cell6_voltage" : 0,
            "cell7_voltage" : 0,
            "cell8_voltage" : 0,
            "cell_average" : 0,
            "cell_range" : 0,
            "pack_temp" : 0,
            "bms_temp" : 0,
            "cfet_temp" : 0,
            "dfet_temp" : 0,
            "board_temp" : 0,
            "status_bits" : [
                True, True, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False,
                False, False, False, False, False, False, False, False
            ]
        }
        self.setv: float = 3.5

    def run(self):
        self.begin_stream(self.exchange)

    def generate_data(self):
        maxcell = 0
        mincell = 5
        packv = 0

        for i in range(1,9):
            cellv = self.put_variation_on_cell_voltage(self.parent.cellvars[i-1].get())
            self.vals[f"cell{i}_voltage"] = cellv
            packv += cellv

            if cellv > maxcell: maxcell = cellv
            if cellv < mincell: mincell = cellv
            
        for i, (key, val) in enumerate(self.parent.tempvars.items()):
            self.vals[f"{key}_temp"] = val.get()

        self.vals['battery_pn'] = self.parent.pnvar.get()
        self.vals['battery_sn'] = self.parent.snvar.get()
        self.vals["pack_current"] = self.parent.currentvar.get()
        self.vals["status_bits"][28] = self.parent.dpovar.get()
        self.vals["pack_voltage"] = round(packv, 3)
        self.vals["cell_average"] = round(packv / 8, 3)
        self.vals["cell_range"] = round(maxcell - mincell, 3)        
        
        if maxcell > 4.25:
            self.vals["status_bits"][0] = False
            self.vals["status_bits"][2] = True
        elif mincell < 2.8:
            self.vals["status_bits"][1] = False
            self.vals["status_bits"][2] = True
        else:
            self.vals["status_bits"][0] = True
            self.vals["status_bits"][1] = True
            self.vals["status_bits"][2] = False
            self.vals["status_bits"][3] = False
        
        if self.vals["pack_current"] > 13:
            self.vals["status_bits"][1] = False
            self.vals["status_bits"][4] = True
        elif self.vals["pack_current"] < -5:
            self.vals["status_bits"][0] = False
            self.vals["status_bits"][5] = True
        else:
            self.vals["status_bits"][4] = False
            self.vals["status_bits"][5] = False


        
    
    def begin_stream(self, exchange_name='data1'):
        print(f"Beginning stream for {self.format_pnsn(self.vals['battery_pn'], self.vals['battery_sn'])} on exchange {exchange_name}")
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
        datastream_channel = connection.channel()
        datastream_channel.exchange_declare(exchange=exchange_name,
                                exchange_type='fanout',
                                auto_delete=True)

        logmsg_channel = connection.channel()
        logmsg_channel.exchange_declare(exchange="log-flags",
                                exchange_type='fanout',
                                auto_delete=True)
        
        logmsg_queue = logmsg_channel.queue_declare(queue='', exclusive=True)
        logmsg_queue_name = logmsg_queue.method.queue
        logmsg_channel.queue_bind(exchange="log-flags", queue=logmsg_queue_name)
        logmsg_channel.basic_consume(queue=logmsg_queue_name,
                                    on_message_callback=self.logmsg_callback,
                                    auto_ack=True)

        try:
            while True:
                time.sleep(1)
                self.generate_data()
                message = json.dumps(self.vals)
                datastream_channel.basic_publish(exchange=exchange_name,
                            routing_key='',
                            body=message)
                if self.logging:
                    self.logger.log(logging.DEBUG, message)
                connection.process_data_events(time_limit=0)
                # print(message)
        except SystemExit:
            print("=================================================================")
            print("Data generation safely killed!")
        finally:
            # print(f"Deleting exchange {exchange_name}...")
            # channel.exchange_delete(exchange_name)
            print(f"Closing channel...")
            datastream_channel.close()
        

    def kill_stream(self):
        # I want to understand exactly how this works. What is happening with the pythonapi call? I know it's from the C API, but how is that working?
        # Reading material on the C API: https://docs.python.org/3/c-api/init.html
        thread_id = 0
        if hasattr(self, '_thread_id'):
            thread_id = self._thread_id
        else:
            for id, thread in threading._active.items():
                if thread is self:
                    thread_id = id
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)

    
    def logmsg_callback(self, ch, method, properties, body):
        message = body.decode('utf-8')
        msg_dict = json.loads(message)

        try:
            self.logging = msg_dict["log-data"]
            self.logger = logging.getLogger(msg_dict["battery-id"])
            self.logger.setLevel(logging.DEBUG)
            csv_handler = logging.FileHandler(msg_dict["logfile-path"])
            csv_handler.setLevel(logging.DEBUG)
            self.logger.addHandler(csv_handler)
            
        except:
            self.logging = False
            self.logger = logging.getLogger("void")



    def put_variation_on_cell_voltage(self, voltage):
        return round(((random.random() - 0.5) *.01 + voltage), 3)    

    def format_pnsn(self, pn, sn):
        return f"{str(pn).rjust(9, "0")} SN{str(sn).rjust(5, "0")}"
            

if __name__ == "__main__":
    exch = 'data1'
    if len(sys.argv) != 2:
        print("You should enter the exchange name as an argument!\ne.g.: 'python.exe data_producer.py data1'\n\nDefaulting to 'data1'...\n\n")
    else:
        exch = sys.argv[1] 

    main: MainWindow = MainWindow(exch)
    main.mainloop()

